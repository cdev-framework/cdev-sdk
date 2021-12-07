from typing import Dict, Union, List, Optional, Set

from pydantic import BaseModel

from cdev.core.constructs.components import ComponentModel, Cdev_Component
from cdev.core.constructs.mapper import CloudMapper


class Resource_State(BaseModel):
    """
    Parent class that describes a namespace that can store resource states via components and also be higher level states for other Resource States 
    """

    uuid: str
    """
    Unique identifier for this state
    """

    parent: Optional['Resource_State']
    """
    The parent namespace above this one
    """

    children: Optional[List['Resource_State']]
    """
    Child namespaces of this one
    """

    components: List[ComponentModel]
    """
    The list of components owned by this namespace
    """



class Resource_State():
    """
    A singleton that encapsulates the configuration and high level information needed to construct the project. This singleton
    can be used within the different components to gain information about the higher level project that it is within. Once constructed,
    the object should remain a read only object to prevent components from changing configuration beyond their scope. 
    """

    _instance = None

    _state = None
    _outputs = {}

    _INSTALLED_COMMANDS = []
    _INSTALLED_COMPONENTS = []
    _INSTALLED_MAPPERS = []

    _parent: Resource_State = None
    _children: List[Resource_State] = []


    def __new__(cls):
        if cls._instance is None:
            #print(f'Creating the Resource State object -> {name}')
            cls._instance = super(Resource_State, cls).__new__(cls)
            # Put any initialization here.
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
        self._state = None
        self._outputs = {}
        self._INSTALLED_COMMANDS = []
        self._INSTALLED_COMPONENTS = []
        self._INSTALLED_MAPPERS = []


    #################
    ##### Components
    #################
    def add_component(self, component: Cdev_Component) -> None:
        if not isinstance(component, Cdev_Component):
            # TODO Throw Error
            print(f"CANT ADD THIS COMPONENT -> {component}")
            raise Exception 
        
        self._INSTALLED_COMPONENTS.append(component)


    def add_components(self, components: List[Cdev_Component]) -> None:
        if not isinstance(components, list):
            raise Exception

        for component in components:
            try:
                self.add_component(component)
            except Exception as e:
                print(e)
        
    
    def get_components(self) -> List[Cdev_Component]:
        return self._INSTALLED_COMPONENTS


    #################
    ##### Mapper
    #################
    def add_mapper(self, mapper: CloudMapper ) -> None:
        if not isinstance(mapper, CloudMapper):
            # TODO Throw error
            print(f"BAD CLOUD MAPPER {mapper}")
            return

        self._INSTALLED_MAPPERS.append(mapper)


    def add_mappers(self, mappers: List[CloudMapper] ) -> None:
        for mapper in mappers:
            self.add_mapper(mapper)

        self._INSTALLED_MAPPERS.append(mapper)


    def get_mappers(self) -> List[CloudMapper]:
        return self._INSTALLED_MAPPERS


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
        self._INSTALLED_COMMANDS.append(command_location)


    def add_commands(self, command_locations: List[str]):
        for command_location in command_locations:
            self.add_command(command_location)

    def get_commands(self) -> List[str]:
        return self._INSTALLED_COMMANDS
    
 
    def clear(self) -> None:
        self._instance = None
        self._components = []
        self._mappers = []
        self._state = None  
        self._outputs = {}    