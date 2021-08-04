"""
Module doc string
"""


from typing import List, Dict, Set, Callable

from .models import Rendered_Component, Resource_State_Difference, Cloud_Output



class Cdev_Component():
    """
    A component is a logical collection of resources. This simple definition is intended to allow flexibility for different
    styles of projects. It is up to the end user to decide on how they group the resources.

    A component must override the `render` method, which returns the desired resources with configuration as a component model. 
    The `render` method does not take any input parameters, therefore all configuration for the component should be done via the `__init__` 
    method. 

    Some properties that components exhibit that can help with determining the best way to group resources are:
    
    - __Information__: Config of other resources will by default be available within a component, but you will be able to explicitly 
    define output that is available for other components to use. 
    - __Triggered deployments__: Any change in a resource within the component will trigger the component to need to be revaluated 
    for changes. This means in a monolothic component, all changes will trigger a re-evaluation on the whole state of the project
    - __Parallelization__: (In the future) rendering components should be able to be parallelized, so using multiple non dependant 
    components  should lead to better total evaluation times.
    """

    def __init__(self, name: str):
        self.name = name
        pass

    def render(self)  -> Rendered_Component:
        """Abstract Class that must be implemented by the descendant that returns a component model"""
        pass

    def get_name(self) -> str:
        return self.name



class CloudMapper():
    """
    A Cloud Mapper is the construct responsible for directly interacting with the Cloud Provider and managing resource state. 
    """
    def __init__(self, resource_to_handler: Dict[str, Callable]) -> None:
        self.resource_to_handler = resource_to_handler
        pass

    def get_namespaces(self) -> List[str]:
        pass

    def deploy_resource(self, resource_diff: Resource_State_Difference) -> bool:
        pass

    def get_available_resources(self) -> Set[str]:
        return set(self.resource_to_handler.keys())

    def get_resource_to_handler(self) -> Dict[str, Callable]:
        return self.resource_to_handler

    def render_resource_outputs(self, resource_diff: Resource_State_Difference) -> Resource_State_Difference:
        return resource_diff


        

class Cdev_Project():
    """
    A singleton that encapsulates the configuration and high level information needed to construct the project. This singleton
    can be used within the different components to gain information about the higher level project that it is within. Once constructed,
    the object should remain a read only object to prevent components from changing configuration beyond their scope. 

    """

    _instance = None
    _components = []
    _mappers = []
    _state = None

    def __new__(cls, name):
        if cls._instance is None:
            #print(f'Creating the Cdev Project object -> {name}')
            cls._instance = super(Cdev_Project, cls).__new__(cls)
            # Put any initialization here.
        else:
            # Raise Error
            print("SECOND TIME")


        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('HAVE NOT CREATED PROJECT OBJECT YET')
        return cls._instance


    def add_component(self, component: Cdev_Component) -> None:
        if not isinstance(component, Cdev_Component):
            # TODO Throw Error
            print(f"CANT ADD THIS COMPONENT -> {component}")
            return 
        
        self._components.append(component)


    def add_components(self, components: List[Cdev_Component]) -> None:
        if not isinstance(components, list):
            return 

        for component in components:
            try:
                self.add_component(component)
            except Exception as e:
                print(e)
        
    
    def get_components(self) -> List[Cdev_Component]:
        return self._components


    def add_mapper(self, mapper: CloudMapper ) -> None:
        if not isinstance(mapper, CloudMapper):
            # TODO Throw error
            print(f"BAD CLOUD MAPPER {mapper}")
            return

        self._mappers.append(mapper)

    def get_mappers(self) -> List[CloudMapper]:
        return self._mappers

    def get_mapper_namespace(self) -> Dict:
        rv = {}

        for mapper in self.get_mappers():
            for namespace in mapper.get_namespaces():
                rv[namespace] = mapper

        return rv







class Cdev_Resource():
    def __init__(self, name: str ) -> None:
        self.name = name
        pass

    def render(self) -> str:
        return "::"

    def from_output(key: str) -> Cloud_Output:
        return Cloud_Output()
