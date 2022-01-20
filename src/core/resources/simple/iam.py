from typing import Dict, List, Optional, Union

from core.utils.types import ImmutableModel


class permission_model(ImmutableModel):
    actions: List[str]
    resource: str
    effect: str
    resource_suffix: Optional[str]


class permission_arn_model(ImmutableModel):
    arn: str



class Permission():
    """
    Permission that can be attached to a resource to give it permission to access other resources.
    """

    def __init__(
        self,
        actions: List[str],
        resource: str,
        effect: str,
        resource_suffix: Optional[str] = "",
    ):
        """
        Arguments:
            actions (List[str]): List of the actions that this policy will include
            resource (str): The Cdev resource id that this policy is for. Note this is not the name in the cloud. A lookup will occur to map the cdev name to aws resource
            effect ('Allow', 'Deny'): Allow or Deny the permission
            resource_suffix (Optional[str]): Some permissions need suffixes added to the looked up aws resource (i.e. dynamodb streams )
        """
        self.actions = actions,
        self.resource = resource,
        self.effect = effect,
        self.resource_suffix = resource_suffix,
            
    def render(self) -> permission_model:
        return permission_model(
            actions=self.actions,
            resource=self.resource,
            effect=self.effect,
            resource_suffix=self.resource_suffix
        )


class PermissionArn():
    """
    Id of a permission that is already deployed on the cloud.
    """
    def __init__(self, arn: str) -> None:
        self.arn = arn


    def render(self) -> permission_arn_model:
        return permission_arn_model(
            arn=self.arn
        )

