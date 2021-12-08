from typing import Dict, Union, List, Optional, Set, Tuple
from cdev.core.constructs.resource import Resource_Difference

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

    parent_uuid: Optional[str]
    """
    The parent namespace above this one
    """

    children: Optional[List[str]]
    """
    Child namespaces of this one
    """

    components: List[ComponentModel]
    """
    The list of components owned by this namespace
    """

    resource_changes: Dict[str, Tuple[str, Resource_Difference]]
    """
    A dictionary of transaction tokens to a tuple of (component_name, diff)
    """

    failed_changes: Dict[str, Tuple[str, Resource_Difference, Dict]]
    """
    A dictionary of transaction tokens to a tuple of (component_name, diff, error_info) for the changes that failed
    """

    def __init__(__pydantic_self__, name: str, uuid: str, components: List[ComponentModel], parent_uuid: Optional[str]=None, children: Optional[List[str]]=None, ) -> None:
        super().__init__(**{
            "name": name,
            "uuid": uuid,
            "components": components,
            "parent_uuid": parent_uuid,
            "children": children
        })