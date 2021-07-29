from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional

from ...models import Cloud_Output, Rendered_Resource







class Tag(BaseModel):

    Key: str

    Value: str







class Policy(Rendered_Resource):
    PolicyName: str

    Path: Optional[str]

    PolicyDocument: str

    Description: Optional[str]

    Tags: Optional[List[Tag]]


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, PolicyName: str, PolicyDocument: str, Path: str=None, Description: str=None, Tags: List[Tag]=None ) -> None:
        super().__init__(**{
            "ruuid": ruuid,
            "name": name,
            "hash": hash,
            "PolicyName": PolicyName,
            "Path": Path,
            "PolicyDocument": PolicyDocument,
            "Description": Description,
            "Tags": Tags,
        })

class Role(Rendered_Resource):
    Path: Optional[str]

    RoleName: str

    AssumeRolePolicyDocument: str

    Description: Optional[str]

    MaxSessionDuration: Optional[int]

    PermissionsBoundary: Optional[str]

    Tags: Optional[List[Tag]]


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, RoleName: str, AssumeRolePolicyDocument: str, Path: str=None, Description: str=None, MaxSessionDuration: int=None, PermissionsBoundary: str=None, Tags: List[Tag]=None ) -> None:
        super().__init__(**{
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
        })
