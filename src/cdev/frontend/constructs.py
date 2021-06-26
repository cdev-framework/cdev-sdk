from sortedcontainers.sortedlist import SortedList, SortedKeyList
from cdev.fs_manager import finder

import hashlib

"""
This file defines the basic constructs that can be used to create projects with Cdev. These constructs are designed to provided the
most basic structure that can then be extended and expanded. 

    Cdev_project:
        - A singleton that encapsulates the configuration and high level information needed to construct the project. This singleton
        can be used within the different components to gain information about the higher level project that it is within. Once constructed,
        the object should remain a read only object to prevent components from changing configuration beyond their scope. 

    Cdev_component:
        - A component is a logical collection of resources. This simple definition is intended to allow flexibility for different
        styles of projects. It is up to the end user to decide on how they group the resources.
        
        A component must override the `render` method, which returns the desired resources with configuration as a json object (schema<>). 
        The `render` method does not take any input parameters, therefore all configuration for the component should be done via the __init__ 
        method. 

        
        Some properties that components exhibit that can help with determining the best way to group resources are:
            - Information: Config of other resources will by default be available within a component, but you will be able to explicitly 
            define output that is available for other components to use. 
            - Triggered deployments: Any change in a resource within the component will trigger the component to need to be revaluated 
            for changes. This means in a monolothic component, all changes will trigger a revaluation on the whole state of the project
            - Parallelization: (In the future) rendering components should be able to be parallelized, so using multiple non dependant 
            components  should lead to better total evaluation times.
"""

class Cdev_Project():
    """
    A singleton that encapsulates the configuration and high level information needed to construct the project. This singleton
    can be used within the different components to gain information about the higher level project that it is within. Once constructed,
    the object should remain a read only object to prevent components from changing configuration beyond their scope. 

    """

    _instance = None
    _components = []
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


    def add_component(self, component):
        if not isinstance(component, Cdev_Component):
            # TODO Throw Error
            print(f"CANT ADD THIS COMPONENT -> {component}")
            return 
        
        self._components.append(component)

    def add_components(self, components):
        if not isinstance(components, list):
            return 

        for component in components:
            try:
                self.add_component(component)
            except Exception as e:
                print(e)
        

    def get_components(self):
        return self._components


class Cdev_Component():
    """
    A component is a logical collection of resources. This simple definition is intended to allow flexibility for different
    styles of projects. It is up to the end user to decide on how they group the resources.

    A component must override the `render` method, which returns the desired resources with configuration as a json object (schema<>). 
    The `render` method does not take any input parameters, therefore all configuration for the component should be done via the `__init__` 
    method. 

    Some properties that components exhibit that can help with determining the best way to group resources are:
    
    - __Information__: Config of other resources will by default be available within a component, but you will be able to explicitly 
    define output that is available for other components to use. 
    - __Triggered deployments__: Any change in a resource within the component will trigger the component to need to be revaluated 
    for changes. This means in a monolothic component, all changes will trigger a revaluation on the whole state of the project
    - __Parallelization__: (In the future) rendering components should be able to be parallelized, so using multiple non dependant 
    components  should lead to better total evaluation times.
    """
    def __init__(self, name: str):
        self.name = name
        pass

    def render(self):
        pass

    def get_name(self) -> str:
        return self.name


class Cdev_FileSystem_Component(Cdev_Component):
    """
        A simple implementation of a Cdev Component that uses a folder on the file system to render the desired resources.
        This component uses provided libraries in Cdev to generate resources. Using this component, you can create serverless
        functions using the provided Cdev annotations that also provides functionality to parse the desired folder out of the 
        file to make it more efficient. 
    """
    def __init__(self, fp, name):
        super().__init__(name)
        self.fp = fp

    def render(self) -> object:
        """Render this component based on the information in the files at the provided folder path"""
        resources_sorted = finder.parse_folder(self.fp, self.get_name())

        appended_hashes = ":".join([x.get("hash") for x in resources_sorted])

        total_component_str = ":".join(appended_hashes)
        
        total_component_hash = hashlib.md5(total_component_str.encode()).hexdigest()

        rv = {
            "rendered_resources": resources_sorted,
            "hash": total_component_hash,
            "name": self.get_name()
        }

        return rv
