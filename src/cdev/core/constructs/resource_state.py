from typing import Dict, Union, List, Optional, Set

from pydantic import BaseModel

from cdev.core.constructs.components import ComponentModel, Component
from cdev.core.constructs.mapper import CloudMapper


class Resource_State(BaseModel):
    """
    Parent class that describes a namespace that can store resource states via components and also be higher level states for other Resource States 
    """

    name: str
    """
    Name for this resource state
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
    pass