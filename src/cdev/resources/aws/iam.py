import typing
from pydantic.main import BaseModel
from enum import Enum
from typing import List

from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher


class policy_model(Rendered_Resource):
    """
    
    [AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_policy)

    Model for IAM policy document
    """
    PolicyName: str
    PolicyDocument: str
    Description: str


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, PolicyName: str, PolicyDocument: str, Description: str, Path="", **kwargs) -> None:
        if kwargs:
            kwargs.update(**{
                "ruuid": ruuid,
                "name": name,
                "hash": hash,
                "PolicyName": PolicyName,
                "PolicyDocument": PolicyDocument,
                "Path": Path,
                "Description": Description,
            })
            super().__init__(**kwargs)
        else:
            super().__init__(**{
                "ruuid": ruuid,
                "name": name,
                "hash": hash,
                "PolicyName": PolicyName,
                "PolicyDocument": PolicyDocument,
                "Path": Path,
                "Description": Description,
            })

    class Config:
        extra='ignore'

class Policy_Output(str, Enum):
    PolicyArn = "TableArn"
    PolicyId = "PolicyId"


class Policy(Cdev_Resource):
    """
    [AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_policy)

    Python class for an AWS IAM Policy
    """

    def __init__(self, name: str, PolicyDocument: str,  PolicyName="", Description="", Path="") -> None:
        super().__init__(name)
        self.PolicyName = PolicyName if PolicyName else name
        self.PolicyDocument = PolicyDocument
        self.Description = Description
        self.Path = Path

        self.hash = hasher.hash_list([self.PolicyName, self.PolicyDocument, self.Path, self.Description])

        
    def render(self):
        return policy_model(**{
            "ruuid": "cdev::aws::iam::policy",
            "name": self.name,
            "hash": self.hash,
            "PolicyName": self.PolicyName,
            "PolicyDocument": self.PolicyDocument,
            "Path": self.Path,
            "Description": self.Description
        })

    def from_output(self, key: Policy_Output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::aws::iam::policy::{self.hash}", "key": key})