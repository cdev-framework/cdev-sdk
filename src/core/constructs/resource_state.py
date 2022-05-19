"""Structure that represents a distinct namespace of cloud resources


"""

from typing import Dict, List, Optional, Tuple
from .resource import Resource_Difference

from pydantic import BaseModel

from .components import ComponentModel


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

    components: Optional[List[ComponentModel]]
    """
    The list of components owned by this namespace
    """

    component_name_to_uuid: Optional[Dict[str, str]]
    """
    A dictionary from the uuid of a component to the component name
    """

    parent_uuid: Optional[str]
    """
    The parent namespace above this one
    """

    children: Optional[List[str]]
    """
    Child namespaces of this one
    """

    resource_changes: Optional[Dict[str, Tuple[str, Resource_Difference]]]
    """
    A dictionary of transaction tokens to a tuple of (component_name, diff)
    """

    failed_changes: Optional[Dict[str, Tuple[str, Resource_Difference, Dict]]]
    """
    A dictionary of transaction tokens to a tuple of (component_name, diff, error_info) for the changes that failed
    """

    def __init__(
        __pydantic_self__,
        name: str,
        uuid: str,
        components: List[ComponentModel] = [],
        component_name_to_uuid: Dict[str, str] = {},
        parent_uuid: Optional[str] = None,
        children: List[str] = [],
        resource_changes: Dict[str, Tuple[str, Resource_Difference]] = {},
        failed_changes: Dict[str, Tuple[str, Resource_Difference, Dict]] = {},
    ) -> None:
        super().__init__(
            **{
                "name": name,
                "uuid": uuid,
                "components": components,
                "component_name_to_uuid": component_name_to_uuid,
                "parent_uuid": parent_uuid,
                "children": children,
                "resource_changes": resource_changes,
                "failed_changes": failed_changes,
            }
        )
