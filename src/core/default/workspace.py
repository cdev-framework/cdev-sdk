from enum import Enum
import importlib
import inspect
import json
import os
import sys
from typing import Callable, List, Dict, Optional, Any, Tuple, Union



from pydantic import BaseModel
from pydantic.types import DirectoryPath, FilePath
from sortedcontainers.sortedlist import SortedList


from ..constructs.resource import Resource_Difference
from ..constructs.backend import Backend, Backend_Configuration, load_backend
from ..constructs.mapper import CloudMapper
from ..constructs.components import Component, Component_Difference, ComponentModel
from ..constructs.commands import BaseCommand, BaseCommandContainer
from ..constructs.workspace import WorkSpace_State, Workspace_Info, Workspace, WorkspaceManager

from ..settings import SETTINGS as cdev_settings

from ..utils.command_finder import find_specified_command, find_unspecified_command




class local_workspace(Workspace):
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

    _state: WorkSpace_State = WorkSpace_State.UNINITIALIZED



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


    def wrap_phase(phase: WorkSpace_State):
        
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



    def initialize_workspace(self, workspace_configuration: Dict):
        self.set_state(WorkSpace_State.INITIALIZING)
        #self.clear_previous_state()
        print(f"loading backend")
        try:
            backend_config = Backend_Configuration( **workspace_configuration.get("backend_configuration"))
            self._backend = load_backend(backend_config)
        except Exception as e:
            print(f"Could not load the load backend")
            raise e
        print(f"Loaded backed")

        self._initialization_file = workspace_configuration.get("initialization_file")
        
    
        # Sometimes the module is already loaded so just reload it to capture any changes
        # Importing the initialization file should cause it to modify the state of the Workspace however is needed
        if sys.modules.get(self._initialization_file):
            importlib.reload(sys.modules.get(self._initialization_file))

        else:
            importlib.import_module(self._initialization_file)

        self.set_state(WorkSpace_State.INITIALIZED)

        
    def clear_previous_state(self):
        self._COMMANDS = []
        self._MAPPERS = []
        self._COMPONENTS = []


    #################
    ##### Mappers
    #################
    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_mapper(self, mapper: CloudMapper ) -> None:
        if not isinstance(mapper, CloudMapper):
            # TODO Throw error
            print(f"BAD CLOUD MAPPER {mapper}")
            return

        self._MAPPERS.append(mapper)


    @wrap_phase(WorkSpace_State.INITIALIZING)
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
    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_command(self, command_location: str):
        self._COMMANDS.append(command_location)


    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_commands(self, command_locations: List[str]):
        """
        This is the adds commands function
        """
        print(f"---- {command_locations}")
        for command_location in command_locations:
            self.add_command(command_location)


    @wrap_phase(WorkSpace_State.INITIALIZED)
    def get_commands(self) -> List[str]:
        return self._COMMANDS


    
    #################
    ##### Components
    #################
    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_component(self, component: Component):
        self._COMPONENTS.append(component)

    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_components(self, components: List[Component]):
        for component in components:
            self.add_component(component)


    @wrap_phase(WorkSpace_State.INITIALIZED)
    def get_components(self) -> List[Component]:
        return self._COMPONENTS

    
    ################
    ##### Initialized
    ################
    
    def set_state(self, value: WorkSpace_State):
        self._state = value


    @wrap_phase(WorkSpace_State.INITIALIZED)
    def get_state(self) -> WorkSpace_State:
        return self._state

    

    
 
    def clear(self) -> None:
        self._instance = None
        self._outputs = {}

        self._MAPPERS = []
        self._COMMANDS = []
        self._COMPONENTS = []


    @wrap_phase(WorkSpace_State.INITIALIZED)
    def execute_command(self, command: str, args: List):
        """
        Find the desired command based on the search path and execute it with the given arguments.

        Args:
            command (str): The full command to search for. can be '.' seperated to denote search path.
            args (List): The command lines arguments to pass to the command.

        Raises:
            KeyError: Raises an exception.
        """
        
        # Command in list form
        command_list = command.split(".")

        # Create list of all directories to start searching in
        all_search_locations_list = self.get_commands()

        if len(command_list) == 1:
            obj, program_name, command_name, is_command = find_unspecified_command(command_list[0], all_search_locations_list)

        else:
            obj, program_name, command_name, is_command = find_specified_command(command_list, all_search_locations_list)


        
        if is_command:
            if not isinstance(obj, BaseCommand):
                raise Exception

            try:
                args = [program_name, command_name, *args]
                obj.run_from_command_line(args)
            except Exception as e:
                raise e

        else:
            if not isinstance(obj, BaseCommandContainer):
                raise Exception
            
            try:
                obj.display_help_message()
            except Exception as e:
                raise e
                
        



class local_workspace_manager(WorkspaceManager):

    def __init__(self, base_dir: DirectoryPath, workspace_dir: str=None, workspace_filename: str=None) -> None:
        self.base_dir = base_dir

        
        self.workspace_dir = workspace_dir if workspace_dir else cdev_settings.get("ROOT_FOLDER_NAME")
        self.workspace_filename = workspace_filename if workspace_filename else cdev_settings.get("WORKSPACE_FILE_NAME")



    def create_new_workspace(self, workspace_info: Workspace_Info):
        """
        Create a new workspace based on the information provided. 

        Args:
            workspace_info (Workspace_Info): information about the backend configuration

        Raises:
            WorkSpaceAlreadyCreated  
        """
        base_cdev_dir = os.path.join(self.base_dir, self.workspace_dir)
        if not os.path.isdir(base_cdev_dir):
            os.mkdir(base_cdev_dir)


        with open(os.path.join(base_cdev_dir, self.workspace_filename), 'w') as fh:
            json.dump(workspace_info.dict(), fh, indent=4)



    def check_if_workspace_exists(self) -> bool:
        return os.path.isfile(os.path.join(self.base_dir, self.workspace_dir, self.workspace_filename))



    def load_workspace_configuration(self) -> Workspace_Info:
        file_location = os.path.join(self.base_dir, self.workspace_dir, self.workspace_filename)

        with open(file_location, 'r') as fh:
            raw_data = json.load(fh)

        try:
            rv = Workspace_Info(**raw_data)

            return rv
        except Exception as e:
            print(e)
            raise e



    def load_workspace(self, config: Workspace_Info) -> local_workspace:
        try:
            if sys.modules.get(config.python_module):
                workspace_module = importlib.reload(sys.modules.get(config.python_module))

            else:
                workspace_module = importlib.import_module(config.python_module)
        except Exception as e:
            print("Error loading workspace module")
            print(f'Error > {e}')

            raise e


        workspace_class = None
        for item in dir(workspace_module):  
            potential_obj = getattr(workspace_module, item)  
            if inspect.isclass(potential_obj) and issubclass(potential_obj, Workspace) and item == config.python_class:
                workspace_class = potential_obj
                break
            
            
        if not workspace_class:
            print(f"Could not find {config.python_class} in {config.python_module}")
            raise Exception

        try:
            # initialize the backend obj with the provided configuration values
            initialized_obj = workspace_class().initialize_workspace(config.config)
        except Exception as e:
            print(f"Could not initialize {workspace_class} Class from config {config.config}")
            raise e

        return initialized_obj
