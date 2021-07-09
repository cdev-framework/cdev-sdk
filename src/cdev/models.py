from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)

from enum import Enum

from pydantic import BaseModel


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

    class Config:
        validate_assignment = True
        extra = 'allow'
        


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
    This is a hash that is used to identify if changes in the resources have occurred. It should have the property:
    - This value changes only if a there is a change in the resource. 
    """


    name: str
    """
    This is a human readable logical name for the component. 

    This value is important for allow human level refactoring of components. To update a component name once created, you must edit only the 
    name and not change the hash. If you change both the hash and name in the same deployment, it will register this as a delete and create 
    instead of update. 
    """



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
