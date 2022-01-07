from enum import Enum
import json
import os
from typing import Any, Dict, List, Optional, TypeVar, Callable

from pydantic import BaseModel
from pydantic.types import DirectoryPath
from core.constructs.backend import Backend_Configuration

from core.constructs.mapper import CloudMapper
from core.constructs.components import Component
from core.constructs.workspace import Workspace_State


from .environment import environment_info, Environment

_GLOBAL_PROJECT = None

class project_info(BaseModel):
    project_name: str
    environments: List[environment_info]
    backend_info: Backend_Configuration
    current_environment: Optional[str]
    settings: Optional[Dict]

    def __init__(__pydantic_self__, project_name: str, environments: List[environment_info], backend_info: Backend_Configuration, current_environment: str=None, settings: Dict={}) -> None:
        """
        Represents the data about a cdev project object:
        
        Parameters:
            project_name (str): Name of the project
            environments (List[environment_info]): The environments that are currently part of the project
            current_environment (str): The current environment 
            settings (Dict): Any setting overrides for the project

        """
        
        super().__init__(**{
            "project_name": project_name,
            "environments": environments,
            "backend_info": backend_info,
            "current_environment": current_environment,
            "settings": settings
        })



class Project_State(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"


F = TypeVar('F', bound=Callable[..., Any])


def wrap_phase(phase: Project_State) -> Callable[[F], F]:
    """
    Annotation that denotes when a function can be executed within the life cycle of a workspace. Throws excpetion if the workspace is not in the correct
    phase. 
    """
    def inner_wrap(func: F) -> F:
        def wrapper_func(project: 'Project', *func_posargs , **func_kwargs):
            
            current_state = project.get_state()
            if not current_state == phase:
                raise Exception(f"Trying to call {func} while in project state {current_state} but need to be in {phase}")

            else:
                
                return func(project, *func_posargs, **func_kwargs) 

        return wrapper_func
    
    return inner_wrap



class Project():
    """
    Global class that defines the functionality for the Project object. The Project object is a global object that is created
    by Cdev to provide access to helpful API's for developers to use in their projects. The object is created and managed by
    the Cdev framework and follows a set of lifecycle rules (link to documentation). 
    
    Developers can access the object in their projects by calling `Project.instance()`. When using the Project Object, developers
    should keep in mind the lifecycle rules around each API and how it fits into their project.

    """
    
    @classmethod
    def instance(cls):
        """
        Method to retrieve the global instance of the Project object. 
        """
        if not _GLOBAL_PROJECT:
            raise Exception("Currently No GLOBAL PROJECT OBJECT")

        return _GLOBAL_PROJECT


    @classmethod
    def set_global_instance(cls, project: 'Project'):
        """
        Method to set the global Project object. Should only be used to as defined in the lifecycle of the Cdev process. (documentation)
        """
        global _GLOBAL_PROJECT
        _GLOBAL_PROJECT = project

    
    @classmethod
    def remove_global_instance(cls, caller: 'Project'):
        """
        Method to reset the Global Project object. This should be the final cleanup step for a Cdev process. 
        """
        global _GLOBAL_PROJECT

        if not _GLOBAL_PROJECT:
            raise Exception("Global Project is not set")


        if not _GLOBAL_PROJECT == caller:
            raise Exception("Only the current Project object can remove itself")

        

        _GLOBAL_PROJECT = None


    def get_state(self) -> Project_State:
        """
        Get the current lifecycle state of the Project. 

        Returns:
            state (Project_State)
        """
        raise NotImplementedError


    def initialize_project(self):
        """
        Initialize the Project object so that it is ready to perform a given operation. Note that any configuration needed for the initialization
        process should be defined during the creation of the object, and set such that this function needs no input. 
        """
        raise NotImplementedError


    def terminate_project(self):
        """
        Terminate the Project object as a cleanup operation after a given operation is complete. This should be the final step in the life cycle
        of an operation that need to initialize the project.
        """
        raise NotImplementedError


    def create_environment(self, environment_name: str):
        """
        Create a new environment for this project.
        """
        raise NotImplementedError


    
    def destroy_environment(self, environment_name: str):
        """
        Destroy an environment. This function should only be called when the project is in the Initialized state, so that
        any cloud resources in the environment will be destroyed. 
        """
        raise NotImplementedError


    def get_all_environment_names(self) -> List[str]:
        """
        Get all the available environments in the Project.

        Returns:
            environment_names (List[str]): environments
        """
        raise NotImplementedError


    def get_current_environment_name(self) -> str:
        """
        Get the environment name that is currently active for this Project.

        Returns:
            environment_name (str)
        """
        raise NotImplementedError


    def set_current_environment(self, environment_name: str):
        """
        Change the currently active environment for this Project. This should only be called when the Project is 
        in the Uninitialized state to prevent it from being called during operations that modify an environment.

        Arguments:
            environment_name (str): The environment name to switch to

        Raises:
            EnvironmentDoesNotExist
        """
        raise NotImplementedError


    def get_environment(self, environment_name: str) -> Environment:
        """
        Get the environment object for a specified environment name. Note that the environment will be in a state 
        based on when this function is called within the Cdev lifecycle. 

        Arguments:
            environment_name (str): The environment name to switch to

        Raises:
            EnvironmentDoesNotExist
        """
        raise NotImplementedError

    def get_current_environment(self) -> Environment:
        """
        Get the environment object for the currently active Environment. Note that the Environment will be in a state 
        based on when this function is called within the Cdev lifecycle. 

        Arguments:
            environment_name (str): The environment name to switch to

        Raises:
            EnvironmentDoesNotExist
        """
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



def check_if_project_exists(base_directory: DirectoryPath) -> bool:
    """
    This function checks for an existing Cdev project at the given directory. A Cdev project is defined by the existence of a valid
    'cdev_project.json' file (can be loaded as project_info) at the location of <base_directory>/.cdev/. 

    Arguments:
        base_directory: Directory to start search from
    """
    
    CDEV_FOLDER = ".cdev"
    CDEV_PROJECT_FILE = "cdev_project.json"

    if not os.path.isdir(base_directory):
        raise Exception(f"Given base directory is not a directory {base_directory}")

    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER)):
        return False

    if not os.path.isfile(os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)):
        return False
    

    try:
        with open(os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE), 'r') as fh:
            project_info(**json.load(fh))

        return True        

    except Exception as e:
        return False




