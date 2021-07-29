from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .dynamodb_models import *



class Table(Rendered_Resource):
    AttributeDefinitions: List[AttributeDefinition]

    TableName: str

    KeySchema: List[KeySchemaElement]

    LocalSecondaryIndexes: Optional[List[LocalSecondaryIndex]]

    GlobalSecondaryIndexes: Optional[List[GlobalSecondaryIndex]]

    BillingMode: Optional[BillingMode] 

    ProvisionedThroughput: Optional[ProvisionedThroughput] 

    StreamSpecification: Optional[StreamSpecification] 

    SSESpecification: Optional[SSESpecification] 

    Tags: Optional[List[Tag]]


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, AttributeDefinitions: List[AttributeDefinition], TableName: str, KeySchema: List[KeySchemaElement], LocalSecondaryIndexes: List[LocalSecondaryIndex]=None, GlobalSecondaryIndexes: List[GlobalSecondaryIndex]=None, ProvisionedThroughput: ProvisionedThroughput=None, StreamSpecification: StreamSpecification=None, SSESpecification: SSESpecification=None, Tags: List[Tag]=None ) -> None:
        super().__init__(**{
            "ruuid": ruuid,
            "name": name,
            "hash": hash,
            "AttributeDefinitions": AttributeDefinitions,
            "TableName": TableName,
            "KeySchema": KeySchema,
            "LocalSecondaryIndexes": LocalSecondaryIndexes,
            "GlobalSecondaryIndexes": GlobalSecondaryIndexes,
            "BillingMode": BillingMode,
            "ProvisionedThroughput": ProvisionedThroughput,
            "StreamSpecification": StreamSpecification,
            "SSESpecification": SSESpecification,
            "Tags": Tags,
        })

    

