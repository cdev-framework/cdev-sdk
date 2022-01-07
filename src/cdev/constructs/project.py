import json
import os
from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic.types import DirectoryPath
from core.constructs.backend import Backend_Configuration

from core.constructs.mapper import CloudMapper
from core.constructs.components import Component


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


class Project():
    """
    A singleton that encapsulates the configuration and high level information needed to construct a project. This singleton
    can be used within the different components to gain information about the higher level project that it is within. 
    """
    
    @classmethod
    def instance(cls):
        if not _GLOBAL_PROJECT:
            raise Exception("Currently No GLOBAL PROJECT OBJECT")

        return _GLOBAL_PROJECT


    @classmethod
    def set_global_instance(cls, project: 'Project'):
        global _GLOBAL_PROJECT
        _GLOBAL_PROJECT = project


    def initialize_project(self):
        raise NotImplementedError


    def create_environment(self, environment_name: str):
        """
        Create a new environment for this project.
        """
        raise NotImplementedError


    def get_all_environment_names(self) -> List[str]:
        raise NotImplementedError


    def get_current_environment_name(self) -> str:
        raise NotImplementedError


    def set_current_environment(self, environment_name: str):
        raise NotImplementedError


    def get_environment(self, environment_name: str) -> Environment:
        raise NotImplementedError

    def get_current_environment(self) -> Environment:
        raise NotImplementedError

    def destroy_environment(self, environment_name: str):
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




