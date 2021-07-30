from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict 

from ...models import Rendered_Resource




class Cors(BaseModel):

    AllowCredentials: bool

    AllowHeaders: List[str]

    AllowMethods: List[str]

    AllowOrigins: List[str]

    ExposeHeaders: List[str]

    MaxAge: int





class ProtocolType(str, Enum): 

    WEBSOCKET = 'WEBSOCKET'

    HTTP = 'HTTP'






class api_output(str, Enum):
    ApiEndpoint = "ApiEndpoint"
    ApiGatewayManaged = "ApiGatewayManaged"
    ApiId = "ApiId"
    ApiKeySelectionExpression = "ApiKeySelectionExpression"
    CorsConfiguration = "CorsConfiguration"
    CreatedDate = "CreatedDate"
    Description = "Description"
    DisableSchemaValidation = "DisableSchemaValidation"
    DisableExecuteApiEndpoint = "DisableExecuteApiEndpoint"
    ImportInfo = "ImportInfo"
    Name = "Name"
    ProtocolType = "ProtocolType"
    RouteSelectionExpression = "RouteSelectionExpression"
    Tags = "Tags"
    Version = "Version"
    Warnings = "Warnings"


class api_model(Rendered_Resource):
    ApiKeySelectionExpression: Optional[str]

    CorsConfiguration: Optional[Cors] 

    CredentialsArn: Optional[str]

    Description: Optional[str]

    DisableSchemaValidation: Optional[bool]

    DisableExecuteApiEndpoint: Optional[bool]

    Name: str

    ProtocolType: ProtocolType 

    RouteKey: Optional[str]

    RouteSelectionExpression: Optional[str]

    Tags: Optional[Dict[str,str]]

    Target: Optional[str]

    Version: Optional[str]


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, Name: str, ProtocolType: ProtocolType, ApiKeySelectionExpression: str=None, CorsConfiguration: Cors=None, CredentialsArn: str=None, Description: str=None, DisableSchemaValidation: bool=None, DisableExecuteApiEndpoint: bool=None, RouteKey: str=None, RouteSelectionExpression: str=None, Tags: Dict[str, str]=None, Target: str=None, Version: str=None ) -> None:
        data = {
            "ruuid": ruuid,
            "name": name,
            "hash": hash,
            "ApiKeySelectionExpression": ApiKeySelectionExpression,
            "CorsConfiguration": CorsConfiguration,
            "CredentialsArn": CredentialsArn,
            "Description": Description,
            "DisableSchemaValidation": DisableSchemaValidation,
            "DisableExecuteApiEndpoint": DisableExecuteApiEndpoint,
            "Name": Name,
            "ProtocolType": ProtocolType,
            "RouteKey": RouteKey,
            "RouteSelectionExpression": RouteSelectionExpression,
            "Tags": Tags,
            "Target": Target,
            "Version": Version,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        super().__init__(**filtered_data)

    class Config:
        extra='ignore'

