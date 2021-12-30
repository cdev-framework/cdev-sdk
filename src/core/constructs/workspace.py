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

_GLOBAL_WORKSPACE: 'Workspace' = None


class Workspace_Info(BaseModel):
    python_module: str
    python_class: str
    config: Dict

    def __init__(__pydantic_self__, python_module: str, python_class: str, config: Dict) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            python_module: The name of the python module to load as the workspace 
            python_class: The name of the class in the python module to initialize
            config: configuration option for the workspace
            
        """
        
        super().__init__(**{
            "python_module": python_module,
            "python_class": python_class,
            "config": config
        })


class Workspace_State(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"


def wrap_phase(phase: Workspace_State):
    """
    Annotation that denotes when a function can be executed within the life cycle of a workspace. Throws excpetion if the workspace is not in the correct
    phase. 
    """
    def inner_wrap(func: Callable)  :
        def wrapper_func(workspace: 'Workspace', *func_posargs , **func_kwargs):
            print(func.__annotations__.get("return"))
            current_state = workspace.get_state()
            if not current_state == phase:
                raise Exception(f"Trying to call {func} while in workspace state {current_state} but need to be in {phase}")

            else:
                
                return func(workspace, *func_posargs, **func_kwargs) 

        return wrapper_func
    
    return inner_wrap


class Workspace():
    """
    A singleton that encapsulates the configuration and high level information needed to construct the project. This singleton
    can be used within the different components to gain information about the higher level project that it is within. Once constructed,
    the object should remain a read only object to prevent components from changing configuration beyond their scope. 
    """
    
    @classmethod
    def instance(cls):
        if not _GLOBAL_WORKSPACE:
            raise Exception("Currently No Global Workspace")

        return _GLOBAL_WORKSPACE


    @classmethod
    def set_global_instance(cls, workspace: 'Workspace'):
        global _GLOBAL_WORKSPACE
        _GLOBAL_WORKSPACE = workspace


    def initialize_workspace(self, workspace_configuration: Workspace_Info):
        """
        Run the configuration needed to initialize a workspace. This should generally only be called by the Core framework itself to ensure that the
        life cycle of a workspace is correctly handled. 
        """
        raise NotImplementedError
        

    def clear_previous_state(self):
        raise NotImplementedError

    #################
    ##### Mappers
    #################
    def add_mapper(self, mapper: CloudMapper ) -> None:
        raise NotImplementedError


    def add_mappers(self, mappers: List[CloudMapper] ) -> None:
       raise NotImplementedError


    def get_mappers(self) -> List[CloudMapper]:
        raise NotImplementedError


    def get_mapper_namespace(self) -> Dict:
        raise NotImplementedError


    #################
    ##### Commands
    #################
    def add_command(self, command_location: str):
        raise NotImplementedError


    def add_commands(self, command_locations: List[str]):
        raise NotImplementedError

    def get_commands(self) -> List[str]:
        raise NotImplementedError


    
    #################
    ##### Components
    #################
    def add_component(self, component: Component):
        raise NotImplementedError


    def add_components(self, components: List[Component]):
        raise NotImplementedError


    def get_components(self) -> List[Component]:
        raise NotImplementedError

    
    ################
    ##### Initialized
    ################
    def get_state(self) -> Workspace_State:
        raise NotImplementedError

    def set_state(self, value: Workspace_State):
        raise NotImplementedError


    ################
    ##### Backend
    ################
    def get_backend(self) -> Backend:
        raise NotImplementedError


    def set_backend(self, backend: Backend):
        raise NotImplementedError


    def execute_command(self, command: str, args: List) -> None:
        """
        Find the desired command based on the search path

        Args:
            command (str): The full command to search for. Can be '.' seperated to denote search path. 
            

        Raises:
            KeyError: Raises an exception.
        """
        
        raise NotImplementedError


    @wrap_phase(Workspace_State.INITIALIZED)
    def generate_current_state(self) -> List[ComponentModel]:
        """
        Execute the components of this workspace to generate the current desired state of the resources.

        Returns:
            Current State (List[ComponentModel]): The current state generated by the components.
        """
        
        rv = []
        components: List[Component] = self.get_components()

        for component in components:
            rv.append(component.render())

        return rv


    def create_state_differences(self, desired_state: List[ComponentModel], previous_state_components: List[str]) -> List[Component_Difference]:
        """
        Produce the differences between the desired state of the components and the 

        Returns:
            Current State (Dict): The current state generated by the components.
        """
        
        raise NotImplementedError


    @wrap_phase(Workspace_State.INITIALIZED)
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
