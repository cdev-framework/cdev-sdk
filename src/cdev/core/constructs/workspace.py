from enum import Enum
import importlib
import inspect
import json
import os
import sys
from typing import Callable, List, Dict, Optional, Any, Tuple, Union
from cdev.core.constructs.resource import Resource_Difference


from pydantic import BaseModel
from pydantic.types import DirectoryPath, FilePath
from sortedcontainers.sortedlist import SortedList

from cdev.core.constructs.backend import Backend, Backend_Configuration, load_backend
from cdev.core.constructs.mapper import CloudMapper
from cdev.core.constructs.components import Component, Component_Difference, ComponentModel


from cdev.core.management.base import BaseCommand, BaseCommandContainer

from cdev.core.settings import SETTINGS as cdev_settings

from cdev.core.utils.exceptions import Cdev_Error, end_process
from cdev.core.utils import hasher as cdev_hasher
from cdev.core.utils.command_finder import find_specified_command, find_unspecified_command



WORKSPACE_INFO_DIR = cdev_settings.get("ROOT_FOLDER_NAME")
WORKSPACE_INFO_FILENAME = cdev_settings.get("WORKSPACE_FILE_NAME")


class Workspace_Info(BaseModel):
    python_module: str
    python_class: str
    config: Dict

    def __init__(__pydantic_self__, python_module: str, python_class: str, config: Dict) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            python_module: The name of the python module to load as the backend 
            config: configuration option for the backend
            
        """
        
        super().__init__(**{
            "python_module": python_module,
            "python_class": python_class,
            "config": config
        })





def create_new_workspace(workspace_info: Workspace_Info, base_dir: DirectoryPath):
    """
    Create a new workspace based on the information provided. 

    Args:
        workspace_info (Workspace_Info): information about the backend configuration

    Raises:
        WorkSpaceAlreadyCreated  
    """
    base_cdev_dir = os.path.join(base_dir, WORKSPACE_INFO_DIR)
    if not os.path.isdir(base_cdev_dir):
        os.mkdir(base_cdev_dir)


    with open(os.path.join(base_cdev_dir, WORKSPACE_INFO_FILENAME), 'w') as fh:
        fh.write(workspace_info.json(indent=4))



def check_if_workspace_exists(base_dir: DirectoryPath) -> bool:
    return os.path.isfile(os.path.join(base_dir, WORKSPACE_INFO_DIR, WORKSPACE_INFO_FILENAME))


def load_workspace_configuration(base_dir: DirectoryPath) -> Workspace_Info:
    file_location = os.path.join(base_dir, WORKSPACE_INFO_DIR, WORKSPACE_INFO_FILENAME)

    with open(file_location, 'r') as fh:
        raw_data = json.load(fh)

    try:
        print(raw_data)
        rv = Workspace_Info(**raw_data)

        return rv
    except Exception as e:
        print(e)
        raise e


class WorkSpace_States(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"


class Workspace():
    """
    A singleton that encapsulates the configuration and high level information needed to construct the project. This singleton
    can be used within the different components to gain information about the higher level project that it is within. Once constructed,
    the object should remain a read only object to prevent components from changing configuration beyond their scope. 
    """
    _instance = None

    _COMMANDS = []
    _MAPPERS = []
    _COMPONENTS = []

    _resource_state_uuid: str = None

    _backend: Backend = None
    _initialization_file = None

    _state: WorkSpace_States = WorkSpace_States.UNINITIALIZED



    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Workspace, cls).__new__(cls)
            # Put any initialization here.

            # Load the backend 
            cls._instance._backend = None
        else:
            # Raise Error
            pass


        return cls._instance


    def wrap_phase(phase: WorkSpace_States):
        
        def inner_wrap(func: Callable):
            def wrapper_func(workspace: 'Workspace', *func_posargs , **func_kwargs):
                print(*func_posargs)
                current_state = Workspace.instance().get_state()
                if not current_state == phase:
                    raise Exception(f"Trying to call {func} while in workspace state {current_state} but need to be in {phase}")

                else:
                    print(f"RIGHT HERE 22 {func} {func_posargs}")
                    func(workspace, *func_posargs, **func_kwargs) 

            return wrapper_func
        
        return inner_wrap



    def initialize_workspace(self, workspace_configuration: Workspace_Info):
        self.set_state(WorkSpace_States.INITIALIZING)
        self.clear_previous_state()
        
        try:
            self._backend = load_backend(workspace_configuration.backend_configuration)
        except Exception as e:
            print(f"Could not load the load backend")
            raise e


        self._initialization_file = workspace_configuration.initialization_file
        
    
        # Sometimes the module is already loaded so just reload it to capture any changes
        # Importing the initialization file should cause it to modify the state of the Workspace however is needed
        if sys.modules.get(self._initialization_file):
            importlib.reload(sys.modules.get(self._initialization_file))

        else:
            importlib.import_module(self._initialization_file)

        self.set_state(WorkSpace_States.INITIALIZED)
        

    @classmethod
    def instance(cls):
        if cls._instance is None:
            Workspace()

        return cls._instance

    
    def clear_previous_state(self):
        self._COMMANDS = []
        self._MAPPERS = []
        self._COMPONENTS = []


    #################
    ##### Mappers
    #################
    @wrap_phase(WorkSpace_States.INITIALIZING)
    def add_mapper(self, mapper: CloudMapper ) -> None:
        if not isinstance(mapper, CloudMapper):
            # TODO Throw error
            print(f"BAD CLOUD MAPPER {mapper}")
            return

        self._MAPPERS.append(mapper)


    @wrap_phase(WorkSpace_States.INITIALIZING)
    def add_mappers(self, mappers: List[CloudMapper] ) -> None:
        for mapper in mappers:
            self.add_mapper(mapper)

        self._MAPPERS.append(mapper)


    def get_mappers(self) -> List[CloudMapper]:
        return self._MAPPERS


    def get_mapper_namespace(self) -> Dict:
        rv = {}

        for mapper in self.get_mappers():
            for namespace in mapper.get_namespaces():
                rv[namespace] = mapper

        return rv


    #################
    ##### Commands
    #################
    @wrap_phase(WorkSpace_States.INITIALIZING)
    def add_command(self, command_location: str):
        self._COMMANDS.append(command_location)


    @wrap_phase(WorkSpace_States.INITIALIZING)
    def add_commands(self, command_locations: List[str]):
        """
        This is the adds commands function
        """
        print(f"---- {command_locations}")
        for command_location in command_locations:
            self.add_command(command_location)


    def get_commands(self) -> List[str]:
        return self._COMMANDS


    
    #################
    ##### Components
    #################
    @wrap_phase(WorkSpace_States.INITIALIZING)
    def add_component(self, component: Component):
        self._COMPONENTS.append(component)

    @wrap_phase(WorkSpace_States.INITIALIZING)
    def add_components(self, components: List[Component]):
        for component in components:
            self.add_component(component)


    def get_components(self) -> List[Component]:
        return self._COMPONENTS

    
    ################
    ##### Initialized
    ################
    def get_state(self) -> WorkSpace_States:
        return self._state

    def set_state(self, value: WorkSpace_States):
        self._state = value

    
 
    def clear(self) -> None:
        self._instance = None
        self._outputs = {}

        self._MAPPERS = []
        self._COMMANDS = []
        self._COMPONENTS = []



    def execute_command(self, command: str) -> Tuple[Union[BaseCommand, BaseCommandContainer], str, str, bool]:
        """
        Find the desired command based on the search path

        Args:
            command (str): The full command to search for. can be '.' seperated to denote search path. 

        Returns:
            command_obj (Union[BaseCommand, BaseCommandContainer]): Initialized command object

        Raises:
            KeyError: Raises an exception.
        """
        
        # Command in list form
        command_list = command.split(".")

        # Create list of all directories to start searching in
        all_search_locations_list = self.get_commands()

        if len(command_list) == 1:
            rv = find_unspecified_command(command_list[0], all_search_locations_list)
            print(rv)
            return rv

        else:
            return find_specified_command(command_list, all_search_locations_list)


        

        


def load_workspace(config: Workspace_Info) -> Workspace:
    try:
        if sys.modules.get(config.python_module):
            backend_module = importlib.reload(sys.modules.get(config.python_module))

        else:
            backend_module = importlib.import_module(config.python_module)
    except Exception as e:
        print("Error loading backend module")
        print(f'Error > {e}')
        
        raise e


    backend_class = None
    for item in dir(backend_module):  
        potential_obj = getattr(backend_module, item)  
        if inspect.isclass(potential_obj) and issubclass(potential_obj, Workspace) and item == config.python_class:
            backend_class = potential_obj
            break
    
    
    if not backend_class:
        print(f"Could not find {config.python_class} in {config.python_module}")
        raise Exception
    
    try:
        # initialize the backend obj with the provided configuration values
        initialized_obj = potential_obj(**config.config)
    except Exception as e:
        print(f"Could not initialize {potential_obj} Class from config {config.config}")
        raise e

    return initialized_obj
    