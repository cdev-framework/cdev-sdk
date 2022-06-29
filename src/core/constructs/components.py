"""Structure that encapsulates a namespace of deploy resources

Properties of a component:
[]
"""

from enum import Enum
from typing import Dict, List, Optional


from pydantic import BaseModel

from .resource import ResourceReferenceModel, ResourceModel


class ComponentModel(BaseModel):
    """

    This is the most basic information needed to describe a rendered component.

    --- Attributes ---

    - resources ->  a list of rendered resources that make up this resource

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

    resources: Optional[List[ResourceModel]]
    """
    List of Rendered Resources that make up the current state of this component
    """

    references: Optional[List[ResourceReferenceModel]]
    """
    A list of the referenced resources used by this component
    """

    cloud_output: Optional[Dict[str, Dict]]
    """
    Output values from the cloud provider of deployed resources
    """

    previous_resolved_cloud_values: Optional[Dict[str, Dict]]
    """
    Previously resolved cloud output
    """

    external_references: Optional[Dict[str, Dict]]
    """
    Dictionary of the resources to information about references to them from other components
    """

    def __init__(
        __pydantic_self__,
        name: str,
        hash: str = "0",
        resources: List[ResourceModel] = [],
        references: List[ResourceReferenceModel] = [],
        cloud_output: Dict[str, Dict] = {},
        previous_resolved_cloud_values: Dict[str, Dict] = {},
        external_references: Dict[str, Dict] = {},
    ) -> None:
        super().__init__(
            **{
                "name": name,
                "hash": hash,
                "resources": list(resources),
                "references": list(references),
                "cloud_output": dict(cloud_output),
                "previous_resolved_cloud_values": dict(previous_resolved_cloud_values),
                "external_references": dict(external_references),
            }
        )


class Component_Change_Type(str, Enum):
    CREATE = "CREATE"
    UPDATE_NAME = "UPDATE_NAME"
    DELETE = "DELETE"
    UPDATE_IDENTITY = "UPDATE_IDENTITY"


class Component_Difference(BaseModel):
    action_type: Component_Change_Type
    previous_name: Optional[str]
    new_name: Optional[str]

    def __init__(
        __pydantic_self__,
        action_type: Component_Change_Type,
        previous_name: str = None,
        new_name: str = None,
    ) -> None:
        super().__init__(
            **{
                "action_type": action_type,
                "previous_name": previous_name,
                "new_name": new_name,
            }
        )

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data
        frozen = True


class Component:
    """
    A component is a logical collection of resources. This simple definition is intended to allow flexibility for different
    styles of setup. It is up to the end user to decide on how they group the resources.

    A component must override the `render` method, which returns the desired resources with configuration as a component model.
    The `render` method does not take any input parameters, therefore all configuration for the component should be done via the `__init__`
    method or other defined methods.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def render(self) -> ComponentModel:
        """Abstract Class that must be implemented by the descendant that returns a component model"""
        raise NotImplementedError

    def get_name(self) -> str:
        return self.name
