"""Structures for representing cloud resources and references within the framework

"""
from functools import wraps
from typing import List, Optional, Any, Dict

from enum import Enum

from core.constructs.models import ImmutableModel, frozendict
from core.constructs.cloud_output import OutputType, Cloud_Output_Str
from core.constructs.types import F
from core.utils.hasher import hash_list
from core.utils.hasher import hash_string


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
    This is a human readable logical name for the resource. This must be unique for the resource within the namespace 
    and resource type (i.e. the concat value of <ruuid>:<name> must be unique)

    This value is important for allow human level refactoring of resources. To update a resources name once created, 
    you must edit only the name and not change the hash. If you change both the hash and name in the same deployment, 
    it will register this as a delete and create instead of update.
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


class TaggableResourceModel(ResourceModel):
    """Derived class, that adds an extra attribute tags.

    Attributes:
        tags: When deploying the resource we add them to it so it can be filtered by any of them
    """

    tags: frozendict
    """
    When deploying the resource we add them to it so it can be filtered by any of them
    
    A typical example is to add a tag per environment name:
     tags = {
        "environment: "prod"
     }
    """


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
    def name(self) -> str:
        """The name of the created resource"""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        raise Exception("The Name of a resource can only be set when initialized.")

    @property
    def ruuid(self) -> str:
        """The ruuid of the created resource"""
        return self._ruuid

    @ruuid.setter
    def ruuid(self, value: str) -> None:
        raise Exception("The Ruuid of a resource can only be set when initialized.")

    @property
    def nonce(self) -> str:
        """The nonce of the created resource"""
        return self._nonce

    @nonce.setter
    def nonce(self, value: str) -> None:
        raise Exception("The nonce of a resource can only be set when initialized.")

    @property
    def hash(self) -> str:
        """The cdev hash of the resource"""
        if self._hash is None:
            raise Exception

        return self._hash

    @hash.setter
    def hash(self, value: str) -> None:
        raise Exception(
            "The `hash` of a Resource can only be set by the `compute_hash` method"
        )

    def compute_hash(self) -> str:
        raise NotImplementedError


class ResourceOutputs:
    """Container object for the returned values from the cloud after the resource has been deployed."""

    OUTPUT_TYPE = OutputType.RESOURCE

    def __init__(self, name: str, ruuid: str) -> None:
        self._name = name
        self._ruuid = ruuid

    @property
    def cloud_id(self) -> "Cloud_Output_Str":
        return Cloud_Output_Str(
            name=self._name, ruuid=self._ruuid, key="cloud_id", type=self.OUTPUT_TYPE
        )

    @cloud_id.setter
    def cloud_id(self, value: Any):
        raise Exception

    @property
    def cloud_region(self) -> "Cloud_Output_Str":
        return Cloud_Output_Str(
            name=self._name,
            ruuid=self._ruuid,
            key="cloud_region",
            type=self.OUTPUT_TYPE,
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
    This is a human readable logical name for the resource. This must be unique for the resource within the namespace 
    and resource type (i.e. the concat value of <ruuid>:<name> must be unique)

    This value is important for allow human level refactoring of resources. To update a resources name once created, 
    you must edit only the name and not change the hash. If you change both the hash and name in the same deployment, 
    it will register this as a delete and create instead of update.
    """

    is_in_parent_resource_state: Optional[bool]
    """
    Boolean to determine if the reference should be resolved in the same resource state or from the parent resource 
    state.
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
    ) -> None:
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
        self._available_permissions = (
            None  # Needs to be set later in the calling subclass
        )

    @property
    def available_permissions(self):
        """The available permissions of the created resource"""
        return self._available_permissions

    @available_permissions.setter
    def available_permissions(self, permissions: Any) -> None:
        self._available_permissions = permissions


class TaggableMixin:
    MAX_TAGS_PER_RESOURCE = 50
    MIN_TAG_NAME_LEN = 1
    MAX_TAG_NAME_LEN = 128
    MIN_TAG_VALUE_LEN = 0
    MAX_TAG_VALUE_LEN = 256

    def __init__(self,  *args, tags: Dict[str, str] = None, **kwargs):
        super().__init__(*args, **kwargs)  # forwards all unused arguments
        self._tags = tags or {}

    @property
    def tags(self) -> Dict[str, str]:
        """The tags of the created resource"""
        return self._tags

    @tags.setter
    def tags(self, value: Dict[str, str]) -> None:
        self._assert_tags_are_valid(value)
        self._tags = value

    def _assert_tags_are_valid(self, tags: Dict[str, str]) -> None:
        """
        Refer to https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html
        The following basic naming and usage requirements apply to tags:
        - Each resource can have a maximum of 50 user created tags.
        - System created tags that begin with aws: are reserved for AWS use, and do not count against this limit.
            You can't edit or delete a tag that begins with the aws: prefix.
        - For each resource, each tag key must be unique, and each tag key can have only one value.
        - The tag key must be a minimum of 1 and a maximum of 128 Unicode characters in UTF-8.
        - The tag value must be a minimum of 0 and a maximum of 256 Unicode characters in UTF-8.
        - Allowed characters can vary by AWS service. For information about what characters
            you can use to tag resources in a particular AWS service, see its documentation.
            In general, the allowed characters are letters, numbers, spaces representable in UTF-8,
            and the following characters: _ . : / = + - @.
        - Tag keys and values are case sensitive. As a best practice, decide on a strategy for capitalizing tags,
            and consistently implement that strategy across all resource types. For example, decide whether to use
            Costcenter, costcenter, or CostCenter, and use the same convention for all tags.
             Avoid using similar tags with inconsistent case treatment.
        """
        if not tags:
            return
        self._assert_tags_count(tags)
        self._assert_tags_properties(tags)

    def _assert_tags_count(self, tags: Dict[str, str]) -> None:
        if len(tags) > self.MAX_TAGS_PER_RESOURCE:
            raise Exception(
                f"Each resource can have a maximum of 50 user created tags. "
                f"Drop at least {(len(tags) - self.MAX_TAGS_PER_RESOURCE)} tags"
            )

    def _assert_tags_properties(self, tags: Dict[str, str]) -> None:
        self._assert_protected_names(tags)
        self._assert_names_length(tags)
        self._assert_values_length(tags)

    def _assert_protected_names(self, tags: Dict[str, str]) -> None:
        invalid_tags = [tag for tag in tags.keys() if tag.startswith("aws")]
        if invalid_tags:
            if len(invalid_tags) > 1:
                raise Exception(
                    f"System created tags that begin with aws: are reserved for AWS use. "
                    f"Please rename the following {', '.join(invalid_tags)}"
                )
            else:
                raise Exception(
                    f"System created tags that begin with aws: are reserved for AWS use. "
                    f"Please rename the following tag {invalid_tags[0]}"
                )

    def _assert_names_length(self, tags: Dict[str, str]) -> None:
        invalid_tags = [
            tag
            for tag in tags.keys()
            if self.MIN_TAG_NAME_LEN > len(tag) > self.MAX_TAG_NAME_LEN
        ]
        if invalid_tags:
            if len(invalid_tags) > 1:
                raise Exception(
                    f"The tag key must be a minimum of {self.MIN_TAG_NAME_LEN} and"
                    f" a maximum of {self.MAX_TAG_NAME_LEN} Unicode characters in UTF-8. "
                    f"Please rename the following {', '.join(invalid_tags)}"
                )
            else:
                raise Exception(
                    f"The tag key must be a minimum of {self.MIN_TAG_NAME_LEN} and"
                    f" a maximum of {self.MAX_TAG_NAME_LEN} Unicode characters in UTF-8. "
                    f"Please rename the following tag {invalid_tags[0]}"
                )

    def _assert_values_length(self, tags: Dict[str, str]) -> None:
        invalid_tags = {
            tag_k: tag_v
            for tag_k, tag_v in tags.items()
            if self.MIN_TAG_VALUE_LEN > len(tag_v) > self.MAX_TAG_VALUE_LEN
        }
        if invalid_tags:
            keys = [tag for tag in invalid_tags.keys()]
            if len(keys) > 1:
                raise Exception(
                    f"The tag value must be a minimum of {self.MIN_TAG_VALUE_LEN} "
                    f"and a maximum of {self.MAX_TAG_VALUE_LEN} Unicode characters in UTF-8. "
                    f"Please change the following tag's value {', '.join(keys)}"
                )
            else:
                raise Exception(
                    f"The tag value must be a minimum of {self.MIN_TAG_VALUE_LEN} "
                    f"and a maximum of {self.MAX_TAG_VALUE_LEN} Unicode characters in UTF-8. "
                    f"Please change the following tag's value {keys[0]}"
                )

    def _get_tags_hash(self) -> str:
        if not self._tags:
            return ""

        return hash_list([hash_string(f"{k}-{v}") for k, v in self._tags.items()])


class PermissionsGrantableMixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)  # forwards all unused arguments
        self._granted_permissions = []  # Needs to be set later in the calling subclass

    @property
    def granted_permissions(self):
        return self._granted_permissions

    @granted_permissions.setter
    @update_hash
    def granted_permissions(self, value: List) -> None:
        self._granted_permissions = value
