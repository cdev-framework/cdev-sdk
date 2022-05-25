"""Set of constructs for adding permissions and authorization

"""

from typing import Dict, FrozenSet, List, Optional, Union

from core.constructs.models import ImmutableModel
from core.constructs.cloud_output import Cloud_Output_Str
from core.constructs.types import cdev_str_model, cdev_str
from core.utils import hasher


class permission_model(ImmutableModel):
    actions: FrozenSet[str]
    cloud_id: cdev_str_model
    effect: str
    resource_suffix: Optional[str]
    hash: str

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data
        frozen = True


class permission_arn_model(ImmutableModel):
    arn: str
    hash: str

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data
        frozen = True


class Permission:
    """
    Permission that can be attached to a resource to give it permission to access other resources.
    """

    def __init__(
        self,
        actions: List[str],
        cloud_id: cdev_str,
        effect: str,
        resource_suffix: Optional[str] = "",
    ) -> None:
        """
        Arguments:
            actions (List[str]): List of the actions that this policy will include
            cloud_id (cdev_str): The cloud id of the resource that is giving the permission
            effect ('Allow', 'Deny'): Allow or Deny the permission
            resource_suffix (Optional[str]): Some permissions need suffixes added to the looked up aws resource (i.e. dynamodb streams )
        """
        self.actions = actions
        self.cloud_id = cloud_id
        self.effect = effect
        self.resource_suffix = resource_suffix

    def render(self) -> permission_model:

        return permission_model(
            actions=frozenset(self.actions),
            cloud_id=self.cloud_id.render()
            if isinstance(self.cloud_id, Cloud_Output_Str)
            else self.cloud_id,
            effect=self.effect,
            hash=self.hash(),
        )

    def hash(self) -> str:
        _hash = hasher.hash_list(
            [
                hasher.hash_list(self.actions),
                self.cloud_id.hash()
                if isinstance(self.cloud_id, Cloud_Output_Str)
                else self.cloud_id,
                self.effect,
            ]
        )

        return _hash


class PermissionArn:
    """
    Id of a permission that is already deployed on the cloud.
    """

    def __init__(self, arn: str) -> None:
        self.arn = arn

    def render(self) -> permission_arn_model:
        return permission_arn_model(arn=self.arn, hash=self.hash())

    def hash(self) -> str:
        return hasher.hash_string(self.arn)
