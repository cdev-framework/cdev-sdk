from enum import Enum
from typing import Dict, Union, List, Optional, Set


from pydantic import BaseModel

from cdev.core.constructs.resource import ResourceModel, Resource_Change_Type, Resource_Difference


class ComponentModel(BaseModel):
    """

    This is the most basic information needed to describe a rendered component. 

    --- Attributes ---

    - rendered_resources ->  a list of rendered resources that make up this resource

    - hash  ->  a string that is the hash of this component. This hash must be computed such that 
                it changes only if a change in the state is desired.

    - name  ->  a string that is the human readable name for this component
    """

    name: str
    """
    A human readable logical name for the component. 

    This value is important for allow human level refactoring of components. To update a component name once created, you must edit only the 
    name and not change the hash. If you change both the hash and name in the same deployment, it will register this as a delete and create 
    instead of update. 
    """

    hash: str
    """
    A hash that is used to identify if changes in the resources have occurred. It should have the property:
    - This value changes only if a there is a change in the resource. 
    """

    rendered_resources: Optional[List[ResourceModel]]
    """
    List of Rendered Resources that make up the current state of this component
    """

    all_parent_resources: Optional[Set[str]]
    """
    A set of all resource identifications (ruuid:hash:<hash> or ruuid:name:<name>) that are a parent resource to some other resource in the component. This set serves as 
    a fast way of checking if we need to update descandants when a resource is updated 
    """

    cloud_output: Optional[Dict[str, Dict]]
    """
    Output values from the cloud provider of deployed resources
    """


    def __init__(__pydantic_self__, name: str, hash: str="0", rendered_resources: List[ResourceModel]=None,  all_parent_resources: Set[str]=None, cloud_output: Dict[str,Dict]=None) -> None:
        super().__init__(**{
            "name": name,
            "hash": hash,
            "rendered_resources": rendered_resources,
            "all_parent_resources": all_parent_resources,
            "cloud_output": cloud_output
        })

    
    def get_parent_resources(self):
        return self.all_parent_resources



class Component_Change_Type(str, Enum):
    CREATE='CREATE'
    UPDATE_NAME='UPDATE_NAME'
    DELETE='DELETE'
 


class Component_Difference(BaseModel):
    action_type: Component_Change_Type
    previous_name: Optional[str]
    new_name: Optional[str]

    class Config:  
        use_enum_values = True


class Component():
    """
    A component is a logical collection of resources. This simple definition is intended to allow flexibility for different
    styles of setup. It is up to the end user to decide on how they group the resources.

    A component must override the `render` method, which returns the desired resources with configuration as a component model. 
    The `render` method does not take any input parameters, therefore all configuration for the component should be done via the `__init__` 
    method or other defined methods. 
    """

    def __init__(self, name: str):
        self.name = name
        pass

    def render(self)  -> ComponentModel:
        """Abstract Class that must be implemented by the descendant that returns a component model"""
        pass

    def get_name(self) -> str:
        return self.name


