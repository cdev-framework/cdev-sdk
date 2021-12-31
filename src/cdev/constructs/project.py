from typing import Dict, List, Optional

from pydantic import BaseModel

from core.constructs.mapper import CloudMapper
from core.constructs.components import Component


from .environment import environment_info, Environment

_GLOBAL_PROJECT = None

class project_info(BaseModel):
    project_name: str
    environments: List[environment_info]
    current_environment: Optional[str]
    settings: Optional[Dict]

    def __init__(__pydantic_self__, project_name: str, environments: List[environment_info], current_environment: str=None, settings: Dict={}) -> None:
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
            "environment_names": environments,
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
    def set_global_instance(cls, workspace: 'Project'):
        global _GLOBAL_PROJECT
        _GLOBAL_PROJECT = workspace


    def create_environment(self, environment_info: environment_info):
        raise NotImplementedError


    def get_all_environments(self) -> List[str]:
        raise NotImplementedError


    def get_current_environment_name(self) -> str:
        raise NotImplementedError


    def set_current_environment(self, environment_name: str):
        raise NotImplementedError


    def get_environment(self, environment_name: str) -> Environment:
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




def create_new_project(project_info: project_info) -> bool:
    pass


def check_if_project_exists() -> bool:
    pass


