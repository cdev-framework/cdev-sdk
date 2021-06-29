from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)

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
    hash: str

    class Config:
        validate_assignment = True
        allow_extra = True


class Rendered_Component(BaseModel):
    """
    This is the most basic information needed to describe a rendered component. 

    --- Attributes ---

    - rendered_resources ->  a list of rendered resources that make up this resource

    - hash  ->  a string that is the hash of this component. This hash must be computed such that 
                it changes only if a change in the state is desired.

    - name  ->  a string that is the human readable name for this component
        
    **BASEMODEL DOCUMENTATION:**
    """

    rendered_resources: List[Rendered_Resource]
    hash: str
    name: str


class Rendered_State(BaseModel):
    """
    This is the most basic information needed to describe a projects rendered state. 

    --- Attributes ---

    - rendered_components ->  a list of rendered components that make up this project

    - hash  ->  a string that is the hash of this component. This hash must be computed such that 
                it changes only if a change in the state is desired.

    **BASEMODEL DOCUMENTATION:**
    """
    rendered_components: List[Rendered_Component]
    hash: str


