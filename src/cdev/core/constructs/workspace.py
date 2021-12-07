import os
from typing import List, Dict, Optional, Any, Tuple


from pydantic import BaseModel
from pydantic.types import DirectoryPath, FilePath
from sortedcontainers.sortedlist import SortedList

from cdev.core.constructs.backend import Backend, Backend_Configuration
from cdev.core.constructs.mapper import CloudMapper
from cdev.core.constructs.components import Component, ComponentModel

from cdev.core.settings import SETTINGS as cdev_settings

from cdev.core.utils.exceptions import Cdev_Error, end_process
from cdev.core.utils import hasher as cdev_hasher


WORKSPACE_INFO_DIR = cdev_settings.get("ROOT_FOLDER_NAME")
WORKSPACE_INFO_FILENAME = cdev_settings.get("WORKSPACE_FILE_NAME")


class Workspace_Info(BaseModel):
    backend_configuration: Backend_Configuration
    initialization_file: Optional[FilePath]


    def __init__(__pydantic_self__, backend_configuration: Backend_Configuration, initialization_file: FilePath=None) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            backend_configuration (Backend_Configuration): configuration information about the backend for this workspaces
            initialization_file (FilePath): python file to load to initialize the workspace 
            
        """
        
        super().__init__(**{
            "backend_configuration": backend_configuration,
            "initialization_file": initialization_file
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



    def __new__(cls, backend_configuration: str):
        if cls._instance is None:
            #print(f'Creating the Resource State object -> {name}')
            cls._instance = super(Workspace, cls).__new__(cls)
            # Put any initialization here.

            # Load the backend 
            cls._instance._backend = backend_configuration
        else:
            # Raise Error
            pass


        return cls._instance


    @classmethod
    def instance(cls):
        if cls._instance is None:
            pass
        return cls._instance

    def clear_previous_state(self):
        self._COMMANDS = []
        self._MAPPERS = []


    def sayHi(self):
        print(self._backend)

    #################
    ##### Mapper
    #################
    def add_mapper(self, mapper: CloudMapper ) -> None:
        if not isinstance(mapper, CloudMapper):
            # TODO Throw error
            print(f"BAD CLOUD MAPPER {mapper}")
            return

        self._MAPPERS.append(mapper)


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
    def add_command(self, command_location: str):
        self._COMMANDS.append(command_location)


    def add_commands(self, command_locations: List[str]):
        for command_location in command_locations:
            self.add_command(command_location)


    def get_commands(self) -> List[str]:
        return self._COMMANDS


    
    #################
    ##### Components
    #################
    def add_component(self, component: Component):
        self._COMPONENTS.append(component)


    def add_components(self, components: List[Component]):
        for component in components:
            self.add_component(component)


    def get_components(self) -> List[Component]:
        return self._COMPONENTS
    
 
    def clear(self) -> None:
        self._instance = None
        self._outputs = {}

        self._MAPPERS = []
        self._COMMANDS = []
        self._COMPONENTS = []


    def execute_frontend(self) -> Tuple[List[ComponentModel], str]:
        """
        This is the function that executes the code to generate a desired state for the project. 

        """

        try:
            ALL_COMPONENTS = self.get_components()
            #log.info(f"Components in project -> {ALL_COMPONENTS}")


            components_sorted: SortedList[ComponentModel] = SortedList(key=lambda x: x.name)
            #log.debug(f"Sorted Components by name -> {project_components_sorted}")

            # Generate the local states
            for component in ALL_COMPONENTS:
                if isinstance(component, Component):
                    rendered_state = component.render()
                    #log.debug(f"component {component} rendered to -> {rendered_state}")
                    components_sorted.add(rendered_state)
                else:
                    raise Cdev_Error(f"{component} is not of type Cdev_Component; Type is {type(Component)} ")

            total_hash = cdev_hasher.hash_list([x.hash for x in components_sorted])


            return components_sorted, total_hash
        except Cdev_Error as e:
            #log.error(e.msg)
            end_process()


