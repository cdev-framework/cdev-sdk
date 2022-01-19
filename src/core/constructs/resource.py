from typing import Dict, TypeVar, Union, List, Optional, Set, Callable, Any
from typing_extensions import Literal

from enum import Enum

from pydantic import BaseModel

from core.utils.types import ImmutableModel

from ..utils.hasher import hash_list


class ResourceModel(ImmutableModel):
    """
    This is the most basic information needed to describe a resource.

    --- Attributes ---

    - ruuid ->  a string that represents the resource identifier (provider::resource-type)

    - hash  ->  a string that is the hash of this object. This hash must be computed such that
                it changes only if a change in the state is desired.
    """

    ruuid: str
    """
    Name space identifier that is used to pass this resource to a downstream mapper

    Form: (top-level-namespace)::(resource-type-id)
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
        extra = "allow"
        frozen = True
        arbitrary_types_allowed = True


    

class ResourceReferenceModel(ImmutableModel):
    """
    This is the information needed to reference a resource that is defined outside this component

    --- Attributes ---

    - ruuid ->  a string that represents the resource identifier (provider::resource-type)

    - hash  ->  a string that is the hash of this object. This hash must be computed such that
                it changes only if a change in the state is desired.
    """

    component_name: str
    """
    Name of the component that this resources resides in
    """

    ruuid: str
    """
    Name space identifier that is used to pass this resource to a downstream mapper

    Form: (top-level-namespace)::(resource-type-id)
    """

    name: str
    """
    This is a human readable logical name for the resource. This must be unique for the resource within the namespace and resource type
    (i.e. the concat value of <ruuid>:<name> must be unique)

    This value is important for allow human level refactoring of resources. To update a resources name once created, you must edit only the 
    name and not change the hash. If you change both the hash and name in the same deployment, it will register this as a delete and create 
    instead of update. 
    """

    is_in_parent_resource_state: Optional[bool]
    """
    Boolean to determine if the reference should be resolved in the same resource state or from the parent resource state.
    """

    def __init__(
        __pydantic_self__,
        component_name: str,
        ruuid: str,
        name: str,
        is_in_parent_resource_state: bool = False,
    ) -> None:
        super().__init__(
            **{
                "component_name": component_name,
                "ruuid": ruuid,
                "name": name,
                "is_in_parent_resource_state": is_in_parent_resource_state,
            }
        )

    class Config:
        extra = "allow"
        frozen = True


class Resource_Change_Type(str, Enum):
    CREATE = "CREATE"
    UPDATE_IDENTITY = "UPDATE_IDENTITY"
    UPDATE_NAME = "UPDATE_NAME"
    DELETE = "DELETE"


class Resource_Reference_Change_Type(str, Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"


class Resource_Difference(ImmutableModel):
    action_type: Resource_Change_Type
    component_name: str
    previous_resource: Optional[ResourceModel]
    new_resource: Optional[ResourceModel]

    def __init__(
        __pydantic_self__,
        action_type: Resource_Change_Type,
        component_name: str,
        previous_resource: ResourceModel = None,
        new_resource: ResourceModel = None,
    ) -> None:
        super().__init__(
            **{
                "action_type": action_type,
                "component_name": component_name,
                "previous_resource": previous_resource,
                "new_resource": new_resource,
            }
        )

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data 
        frozen = True


class Resource_Reference_Difference(ImmutableModel):
    action_type: Resource_Reference_Change_Type
    originating_component_name: str
    resource_reference: ResourceReferenceModel

    def __init__(
        __pydantic_self__,
        action_type: Resource_Reference_Change_Type,
        originating_component_name: str,
        resource_reference: ResourceReferenceModel,
    ) -> None:
        super().__init__(
            **{
                "action_type": action_type,
                "originating_component_name": originating_component_name,
                "resource_reference": resource_reference,
            }
        )

    class Config:
        use_enum_values = True
        frozen = True

    
Output_Type = Union[Literal['resource'], Literal['reference']]


class Cloud_Output(BaseModel):
    """
    Often we want resources that depend on the value of output of other resources that is only known after a cloud resource is created. This servers
    as an placeholder for that desired value until it is available.
    """

    ruuid: str
    """
    Ruuid of the resource
    """

    name: str
    """
    Name of the resource
    """

    key: str
    """
    The key to lookup the output value by (ex: arn)
    """

    type: Output_Type


    id: str


    component_name: Optional[str]

    def __str__(self) -> str:
        return f"{self.ruuid}$${self.name}$${self.key}"


    def __init__(__pydantic_self__, ruuid: str, name: str, key: str, type: Output_Type, component_name: str = None, id: str=None) -> None:
        super().__init__(**{
            "ruuid": ruuid,
            "name": name,
            "key": key,
            "type": type,
            "id": 'cdev_output',
            "component_name": component_name
        })


class Resource:
    RUUID: str = None

    def __init__(self, name: str):
        self.name = name

    def render(self) -> ResourceModel:
        pass

    def from_output(self, key: Enum) -> Cloud_Output:
        return Cloud_Output(
            ruuid= self.RUUID,
            name= self.name,
            key= key.value,
            type= 'resource'
        )


class Resource_Reference:
    RUUID: str = None

    def __init__(
        self, component_name: str, name: str, is_in_parent_resource_state: bool = False
    ):
        self.component_name = component_name
        self.name = name
        self.is_in_parent_resource_state = is_in_parent_resource_state

    def render(self) -> ResourceReferenceModel:
        raise NotImplementedError

    def from_output(self, key: Enum) -> Cloud_Output:
        return Cloud_Output(
            ruuid= self.RUUID,
            name= self.name,
            key= key.value,
            type= 'reference',
            component_name= self.component_name
        )

    def compute_hash(self) -> str:
        return hash_list(
            [
                self.component_name,
                self.RUUID,
                self.name,
                str(self.is_in_parent_resource_state),
            ]
        )
