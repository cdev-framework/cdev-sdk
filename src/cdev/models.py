from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)

from enum import Enum
from typing_extensions import Literal

from pydantic import BaseModel
from pydantic.types import constr


class Rendered_Resource(BaseModel):
    """
    This is the most basic information needed to describe a rendered resource. 

    --- Attributes ---

    - ruuid ->  a string that represents the resource identifier (provider::resource-type)

    - hash  ->  a string that is the hash of this object. This hash must be computed such that 
                it changes only if a change in the state is desired.
        
    **BASEMODEL DOCUMENTATION:**
    """


    ruuid: str
    """
    Name space indemnificator that is used to pass this resource to a downstream mapper

    Form: (top-level-namespace):(resource-type-id)
    """


    hash: str
    """
    This is a hash that is used to identify if changes in the resources have occurred. It should have the property:
    - This value changes only if a there is a change in the resource. 
    """


    name: str
    """
    This is a human readable logical name for the resource. This must be unique for the resource within the namespace and resource type
    (i.e. the concat value of <ruuid>:<name> must be unique)

    This value is important for allow human level refactoring of resources. To update a resources name once created, you must edit only the 
    name and not change the hash. If you change both the hash and name in the same deployment, it will register this as a delete and create 
    instead of update. 
    """

    parent_resources: Optional[List[str]]
    """
    A set of all resource identifications (ruuid:hash) that are a parent resource to some other resource in the component. This set serves as 
    a fast way of checking if we need to update descandants when a resource is updated 
    """

    class Config:
        validate_assignment = True
        extra = 'allow'


    def get_parent_resources(self) -> List[str]:
        """
        This function returns any resources that this resources depeneds on via the Output mechanism
        """
        return None


class Cloud_Output(BaseModel):
    """
    Often we want resources that depend on the value of output of other resoures that is only known after a cloud resource is created. This servers
    as an placeholder for that desired value until it is available. 
    """

    resource: str
    """
    ruuid:hash
    """

    key: str
    """
    The key to lookup the output value by (ex: arn)
    """

    type: Literal["cdev_output"]
        
    def __str__(self) -> str:
        return f"{self.resource}$${self.key}"

    


class Rendered_Component(BaseModel):
    """
    **Rendered_Resource**

    This is the most basic information needed to describe a rendered component. 

    --- Attributes ---

    - rendered_resources ->  a list of rendered resources that make up this resource

    - hash  ->  a string that is the hash of this component. This hash must be computed such that 
                it changes only if a change in the state is desired.

    - name  ->  a string that is the human readable name for this component
        
    **BASEMODEL DOCUMENTATION:**
    """



    rendered_resources: Union[List[Rendered_Resource], None]
    """
    List of Rendered Resources that make up the current state of this component
    """


    hash: str
    """
    A hash that is used to identify if changes in the resources have occurred. It should have the property:
    - This value changes only if a there is a change in the resource. 
    """


    name: str
    """
    A human readable logical name for the component. 

    This value is important for allow human level refactoring of components. To update a component name once created, you must edit only the 
    name and not change the hash. If you change both the hash and name in the same deployment, it will register this as a delete and create 
    instead of update. 
    """

    all_parent_resources: Optional[Set[str]]
    """
    A set of all resource identifications (ruuid:hash) that are a parent resource to some other resource in the component. This set serves as 
    a fast way of checking if we need to update descandants when a resource is updated 
    """

    
    def get_parent_resources(self):
        return self.all_parent_resources



class Rendered_State(BaseModel):
    """
    This is the most basic information needed to describe a projects rendered state. 

    --- Attributes ---

    - rendered_components ->  a list of rendered components that make up this project

    - hash  ->  a string that is the hash of this component. This hash must be computed such that 
                it changes only if a change in the state is desired.

    **BASEMODEL DOCUMENTATION:**
    """
    rendered_components: Union[List[Rendered_Component], None]
    hash: str



class Action_Type(str, Enum):
    CREATE='CREATE'
    UPDATE_IDENTITY='UPDATE_IDENTITY'
    UPDATE_NAME='UPDATE_NAME'
    DELETE='DELETE'



class Resource_State_Difference(BaseModel):
    action_type: Action_Type
    previous_resource: Union[Rendered_Resource, None]
    new_resource: Union[Rendered_Resource, None]

    class Config:  
        use_enum_values = True


class Component_State_Difference(BaseModel):
    action_type: Action_Type
    previous_component: Union[Rendered_Component, None]
    new_component: Union[Rendered_Component, None]

    resource_diffs: Union[List[Resource_State_Difference], None]

    class Config:  
        use_enum_values = True


