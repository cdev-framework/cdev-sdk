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


from .resource import Resource_Difference
from .backend import Backend, Backend_Configuration, load_backend
from .mapper import CloudMapper
from .components import Component, Component_Difference, ComponentModel


from .commands import BaseCommand, BaseCommandContainer

from ..settings import SETTINGS as cdev_settings


from ..utils.command_finder import find_specified_command, find_unspecified_command



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


class WorkSpace_State(str, Enum):
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
                

                current_state = Workspace.instance().get_state()
                if not current_state == phase:
                    raise Exception(f"Trying to call {func} while in workspace state {current_state} but need to be in {phase}")

                else:
                    print(f"RIGHT HERE 22 {func} {func_posargs}")
                    func(workspace, *func_posargs, **func_kwargs) 

            return wrapper_func
        
        return inner_wrap

    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            Workspace()

        return cls._instance



    def initialize_workspace(self, workspace_configuration: Workspace_Info):
        raise NotImplementedError
        

    
    def clear_previous_state(self):
        raise NotImplementedError

    #################
    ##### Mappers
    #################
    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_mapper(self, mapper: CloudMapper ) -> None:
        raise NotImplementedError


    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_mappers(self, mappers: List[CloudMapper] ) -> None:
       raise NotImplementedError


    def get_mappers(self) -> List[CloudMapper]:
        raise NotImplementedError


    def get_mapper_namespace(self) -> Dict:
        raise NotImplementedError


    #################
    ##### Commands
    #################
    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_command(self, command_location: str):
        raise NotImplementedError

    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_commands(self, command_locations: List[str]):
        raise NotImplementedError

    def get_commands(self) -> List[str]:
        raise NotImplementedError


    
    #################
    ##### Components
    #################
    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_component(self, component: Component):
        raise NotImplementedError

    @wrap_phase(WorkSpace_State.INITIALIZING)
    def add_components(self, components: List[Component]):
        raise NotImplementedError


    def get_components(self) -> List[Component]:
        raise NotImplementedError

    
    ################
    ##### Initialized
    ################
    def get_state(self) -> WorkSpace_State:
        raise NotImplementedError

    def set_state(self, value: WorkSpace_State):
        raise NotImplementedError

    @wrap_phase(WorkSpace_State.INITIALIZED)
    def execute_command(self, command: str, args: List) -> Tuple[Union[BaseCommand, BaseCommandContainer], str, str, bool]:
        """
        Find the desired command based on the search path

        Args:
            command (str): The full command to search for. can be '.' seperated to denote search path. 

        Returns:
            command_obj (Union[BaseCommand, BaseCommandContainer]): Initialized command object

        Raises:
            KeyError: Raises an exception.
        """
        
        raise NotImplementedError

        

class WorkspaceManager:
    def create_new_workspace(self, workspace_info: Workspace_Info, *posargs, **kwargs):
        """
        Create a new workspace based on the information provided. 
    
        Args:
            workspace_info (Workspace_Info): information about the backend configuration
    
        Raises:
            WorkSpaceAlreadyCreated  
        """
        raise NotImplementedError


    def check_if_workspace_exists(self, *posargs, **kwargs) -> bool:
        raise NotImplementedError


    def load_workspace_configuration(self, *posargs, **kwargs) -> Workspace_Info:
        raise NotImplementedError

    
    def load_workspace(self, *posargs, **kwargs) -> Workspace:
        raise NotImplementedError
