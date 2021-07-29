from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional

from ...models import Cloud_Output, Rendered_Resource


class ScalarAttributeType(str, Enum): 

    S = 'S'

    N = 'N'

    B = 'B'


class AttributeDefinition(BaseModel):

    AttributeName: str

    AttributeType: ScalarAttributeType 



class KeyType(str, Enum): 

    HASH = 'HASH'

    RANGE = 'RANGE'


class KeySchemaElement(BaseModel):

    AttributeName: str

    KeyType: KeyType 



class ProjectionType(str, Enum): 

    ALL = 'ALL'

    KEYS_ONLY = 'KEYS_ONLY'

    INCLUDE = 'INCLUDE'



class Projection(BaseModel):

    ProjectionType: ProjectionType 

    NonKeyAttributes: List[str]


class LocalSecondaryIndex(BaseModel):

    IndexName: str

    KeySchema: List[KeySchemaElement]

    Projection: Projection 


class ProvisionedThroughput(BaseModel):

    ReadCapacityUnits: int

    WriteCapacityUnits: int


class GlobalSecondaryIndex(BaseModel):

    IndexName: str

    KeySchema: List[KeySchemaElement]

    Projection: Projection 

    ProvisionedThroughput: ProvisionedThroughput 


class BillingMode(str, Enum): 

    PROVISIONED = 'PROVISIONED'

    PAY_PER_REQUEST = 'PAY_PER_REQUEST'


class StreamViewType(str, Enum): 

    NEW_IMAGE = 'NEW_IMAGE'

    OLD_IMAGE = 'OLD_IMAGE'

    NEW_AND_OLD_IMAGES = 'NEW_AND_OLD_IMAGES'

    KEYS_ONLY = 'KEYS_ONLY'


class StreamSpecification(BaseModel):

    StreamEnabled: bool

    StreamViewType: StreamViewType 


class SSEType(str, Enum): 

    AES256 = 'AES256'

    KMS = 'KMS'



class SSESpecification(BaseModel):

    Enabled: bool

    SSEType: SSEType 

    KMSMasterKeyId: str




class Tag(BaseModel):

    Key: str

    Value: str


class UpdateGlobalSecondaryIndexAction(BaseModel):

    IndexName: str

    ProvisionedThroughput: ProvisionedThroughput 


class CreateGlobalSecondaryIndexAction(BaseModel):

    IndexName: str

    KeySchema: List[KeySchemaElement]

    Projection: Projection 

    ProvisionedThroughput: ProvisionedThroughput 


class DeleteGlobalSecondaryIndexAction(BaseModel):

    IndexName: str


class GlobalSecondaryIndexUpdate(BaseModel):

    Update: UpdateGlobalSecondaryIndexAction 

    Create: CreateGlobalSecondaryIndexAction 

    Delete: DeleteGlobalSecondaryIndexAction 



class ProvisionedThroughputOverride(BaseModel):

    ReadCapacityUnits: int


class ReplicaGlobalSecondaryIndex(BaseModel):

    IndexName: str

    ProvisionedThroughputOverride: ProvisionedThroughputOverride 


class CreateReplicationGroupMemberAction(BaseModel):

    RegionName: str

    KMSMasterKeyId: str

    ProvisionedThroughputOverride: ProvisionedThroughputOverride 

    GlobalSecondaryIndexes: List[ReplicaGlobalSecondaryIndex]


class UpdateReplicationGroupMemberAction(BaseModel):

    RegionName: str

    KMSMasterKeyId: str

    ProvisionedThroughputOverride: ProvisionedThroughputOverride 

    GlobalSecondaryIndexes: List[ReplicaGlobalSecondaryIndex]


class DeleteReplicationGroupMemberAction(BaseModel):

    RegionName: str


class ReplicationGroupUpdate(BaseModel):

    Create: CreateReplicationGroupMemberAction 

    Update: UpdateReplicationGroupMemberAction 

    Delete: DeleteReplicationGroupMemberAction 




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


    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, AttributeDefinitions: List[AttributeDefinition], TableName: str, KeySchema: List[KeySchemaElement], LocalSecondaryIndexes: List[LocalSecondaryIndex]=None, GlobalSecondaryIndexes: List[GlobalSecondaryIndex]=None, BillingMode: BillingMode=None, ProvisionedThroughput: ProvisionedThroughput=None, StreamSpecification: StreamSpecification=None, SSESpecification: SSESpecification=None, Tags: List[Tag]=None ) -> None:
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
