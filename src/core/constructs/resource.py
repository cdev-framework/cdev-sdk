"""Structures for representing cloud resources and references within the framework

"""
from functools import wraps
from typing import Dict, TypeVar, Union, List, Optional, Set, Callable, Any

from enum import Enum

from core.constructs.models import ImmutableModel
from core.constructs.cloud_output import OutputType, Cloud_Output_Str
from core.constructs.types import F

from ..utils.hasher import hash_list

    
##################
##### Resource
##################
class ResourceModel(ImmutableModel):
    """Base class with basic information about a defined resource.
    
    All classes derived from this should contain additional information about the state of a resource. 
    Within the life cycle of the Cdev Core framework,this is used to represent resources after any
    configuration; hence the need to make these immutable data
    classes. 

    Attributes:
        name: The name of the resource. Note that the combination of a name and ruuid should be unique 
          within a namespace
        ruuid: The identifier of this resource type.
        hash: A string that is the hash of this object. This hash must be computed such that it changes 
          only if a change in the state is desired.
    """

    name: str
    """
    This is a human readable logical name for the resource. This must be unique for the resource within the namespace and resource type
    (i.e. the concat value of <ruuid>:<name> must be unique)

    This value is important for allow human level refactoring of resources. To update a resources name once created, you must edit only the 
    name and not change the hash. If you change both the hash and name in the same deployment, it will register this as a delete and create 
    instead of update. 
    """

    ruuid: str
    """
    Name space identifier that is used to pass this resource to a downstream mapper

    Form: (top-level-namespace)::(resource-type-id)
    """

    hash: str
    """
    This is a hash that is used to identify if changes in the resources have occurred.
    """

    class Config:
        arbitrary_types_allowed = True


class Resource_Change_Type(str, Enum):
    CREATE = "CREATE"
    UPDATE_IDENTITY = "UPDATE_IDENTITY"
    UPDATE_NAME = "UPDATE_NAME"
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


def update_hash(func: F) -> F:
    """Wrap a function that modifies the state of a Resource so that the hash is properly updated when a change occurs.

    Args:
        func (F): State modifying method.

    Returns:
        F: Wrapped function to compute new hash after changes have been made
    """
    @wraps(func)
    def wrapped_func(resource: "Resource", *func_posargs, **func_kwargs):
        rv = func(resource, *func_posargs, **func_kwargs)
        resource.compute_hash()
        return rv

    return wrapped_func


class Resource:
    def __init__(self, name: str, ruuid: str, nonce: str = ""):
        self._name = name
        self._ruuid = ruuid
        self._hash = None
        self._nonce = nonce

    def render(self) -> ResourceModel:
        raise NotImplementedError

    @property
    def name(self):
        """The name of the created resource"""
        return self._name

    @name.setter
    def name(self, value: str):
        raise Exception("The Name of a resource can only be set when initialized.")

    @property
    def ruuid(self):
        """The ruuid of the created resource"""
        return self._ruuid

    @ruuid.setter
    def ruuid(self, value: str):
        raise Exception("The Ruuid of a resource can only be set when initialized.")

    @property
    def nonce(self):
        """The nonce of the created resource"""
        return self._nonce

    @nonce.setter
    def nonce(self, value: str):
        raise Exception("The nonce of a resource can only be set when initialized.")

    @property
    def hash(self):
        """The cdev hash of the resource"""
        if self._hash is None:
            raise Exception

        return self._hash

    @hash.setter
    def hash(self, value: str):
        raise Exception("The `hash` of a Resource can only be set by the `compute_hash` method")

    def compute_hash(self):
        raise NotImplementedError


class ResourceOutputs():
    """Container object for the returned values from the cloud after the resource has been deployed."""
    OUTPUT_TYPE = OutputType.RESOURCE

    def __init__(self, name: str, ruuid: str) -> None:
        self._name = name
        self._ruuid = ruuid

    @property
    def cloud_id(self) -> 'Cloud_Output_Str':
        return Cloud_Output_Str(
            name=self._name,
            ruuid=self._ruuid,
            key='cloud_id',
            type=self.OUTPUT_TYPE
        )

    @cloud_id.setter
    def cloud_id(self, value: Any):
        raise Exception

    @property
    def cloud_region(self) -> 'Cloud_Output_Str':
        return Cloud_Output_Str(
            name=self._name,
            ruuid=self._ruuid,
            key='cloud_region',
            type=self.OUTPUT_TYPE
        )

    @cloud_region.setter
    def cloud_region(self, value: Any):
        raise Exception

##################
##### Reference
##################

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


class Resource_Reference_Change_Type(str, Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"


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

    def compute_hash(self) -> str:
        return hash_list(
            [
                self.component_name,
                self.RUUID,
                self.name,
                str(self.is_in_parent_resource_state),
            ]
        )



####################
##### Mixins
####################
class PermissionsAvailableMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # forwards all unused arguments
        self._available_permissions = None # Needs to be set later in the calling subclass

    @property
    def available_permissions(self):
        """The available permissions of the created resource"""
        return self._available_permissions

    @available_permissions.setter
    def available_permissions(self, permissions: Any):
        self._available_permissions = permissions



class PermissionsGrantableMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # forwards all unused arguments
        self._granted_permissions = [] # Needs to be set later in the calling subclass


    @property
    def granted_permissions(self):
        return self._granted_permissions

    @granted_permissions.setter
    @update_hash
    def granted_permissions(self, value: List):
        self._granted_permissions = value
