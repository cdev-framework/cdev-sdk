from typing import Dict, List, Optional, Union

from pydantic.main import BaseModel

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher




class Permission(BaseModel):
    actions: List[str]
    resource: str
    effect: str
    resource_suffix: Optional[str]

    def __init__(
        self,
        actions: List[str],
        resource: str,
        effect: str,
        resource_suffix: Optional[str] = "",
    ):
        """
        Create a permission object that can be attached to a lambda function to give it permission to access other resources.

        args:
            actions (List[str]): List of the IAM actions that this policy will include
            resource (str): The Cdev resource name that this policy is for. Note this is not the aws resource name. A lookup will occur to map the cdev name to aws resource
            effect ('Allow', 'Deny'): Allow or Deny the permission
            resource_suffix (Optional[str]): Some permissions need suffixes added to the looked up aws resource (i.e. dynamodb streams )
        """
        super().__init__(
            **{
                "actions": actions,
                "resource": resource,
                "effect": effect,
                "resource_suffix": resource_suffix,
            }
        )

    def get_hash(self) -> str:
        return hasher.hash_list(
            [
                self.resource,
                hasher.hash_list(self.actions),
                self.effect,
                self.resource_suffix,
            ]
        )


class PermissionArn(BaseModel):
    arn: str

    def get_hash(self) -> str:
        return hasher.hash_string(self.arn)
