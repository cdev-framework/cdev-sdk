from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict 

from ...models import Rendered_Resource







class Tag(BaseModel):

    Key: str

    Value: str







class policy_output(str, Enum):
    PolicyName = "PolicyName"
    PolicyId = "PolicyId"
    Arn = "Arn"
    Path = "Path"
    DefaultVersionId = "DefaultVersionId"
    AttachmentCount = "AttachmentCount"
    PermissionsBoundaryUsageCount = "PermissionsBoundaryUsageCount"
    IsAttachable = "IsAttachable"
    Description = "Description"
    CreateDate = "CreateDate"
    UpdateDate = "UpdateDate"
    Tags = "Tags"


class role_output(str, Enum):
    Path = "Path"
    RoleName = "RoleName"
    RoleId = "RoleId"
    Arn = "Arn"
    CreateDate = "CreateDate"
    AssumeRolePolicyDocument = "AssumeRolePolicyDocument"
    Description = "Description"
    MaxSessionDuration = "MaxSessionDuration"
    PermissionsBoundary = "PermissionsBoundary"
    Tags = "Tags"
    RoleLastUsed = "RoleLastUsed"


class policy_model(Rendered_Resource):
    PolicyName: str

    Path: Optional[str]

    PolicyDocument: str

    Description: Optional[str]

    Tags: Optional[List[Tag]]


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, PolicyName: str, PolicyDocument: str, Path: str=None, Description: str=None, Tags: List[Tag]=None ) -> None:
        data = {
            "ruuid": ruuid,
            "name": name,
            "hash": hash,
            "PolicyName": PolicyName,
            "Path": Path,
            "PolicyDocument": PolicyDocument,
            "Description": Description,
            "Tags": Tags,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        super().__init__(**filtered_data)

    class Config:
        extra='ignore'

class role_model(Rendered_Resource):
    Path: Optional[str]

    RoleName: str

    AssumeRolePolicyDocument: str

    Description: Optional[str]

    MaxSessionDuration: Optional[int]

    PermissionsBoundary: Optional[str]

    Tags: Optional[List[Tag]]


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, RoleName: str, AssumeRolePolicyDocument: str, Path: str=None, Description: str=None, MaxSessionDuration: int=None, PermissionsBoundary: str=None, Tags: List[Tag]=None ) -> None:
        data = {
            "ruuid": ruuid,
            "name": name,
            "hash": hash,
            "Path": Path,
            "RoleName": RoleName,
            "AssumeRolePolicyDocument": AssumeRolePolicyDocument,
            "Description": Description,
            "MaxSessionDuration": MaxSessionDuration,
            "PermissionsBoundary": PermissionsBoundary,
            "Tags": Tags,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        super().__init__(**filtered_data)

    class Config:
        extra='ignore'

