from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict 

from ...models import Cloud_Output, Rendered_Resource


class ScalarAttributeType(str, Enum): 


    S = 'S'
    
    N = 'N'
    
    B = 'B'
    

class AttributeDefinition(BaseModel):
    """
    Represents an attribute for describing the key schema for the table and indexes.


    """


    AttributeName: str
    """
    A name for the attribute.


    """

    AttributeType: ScalarAttributeType 
    """
    The data type for the attribute, where:

 *  `S` - the attribute is of type String


*  `N` - the attribute is of type Number


*  `B` - the attribute is of type Binary



    """


    def __init__(self, AttributeName: str, AttributeType: ScalarAttributeType ):
        "My doc string"
        super().__init__(**{
            "AttributeName": AttributeName,
            "AttributeType": AttributeType,
        })        




class KeyType(str, Enum): 


    HASH = 'HASH'
    
    RANGE = 'RANGE'
    

class KeySchemaElement(BaseModel):
    """
    Represents *a single element* of a key schema. A key schema specifies the attributes that make up the primary key of a table, or the key attributes of an index.

 A `KeySchemaElement` represents exactly one attribute of the primary key. For example, a simple primary key would be represented by one `KeySchemaElement` (for the partition key). A composite primary key would require one `KeySchemaElement` for the partition key, and another `KeySchemaElement` for the sort key.

 A `KeySchemaElement` must be a scalar, top-level attribute (not a nested attribute). The data type must be one of String, Number, or Binary. The attribute cannot be nested within a List or a Map.


    """


    AttributeName: str
    """
    The name of a key attribute.


    """

    KeyType: KeyType 
    """
    The role that this key attribute will assume:

 *  `HASH` - partition key


*  `RANGE` - sort key



  The partition key of an item is also known as its *hash attribute*. The term "hash attribute" derives from DynamoDB's usage of an internal hash function to evenly distribute data items across partitions, based on their partition key values.

 The sort key of an item is also known as its *range attribute*. The term "range attribute" derives from the way DynamoDB stores items with the same partition key physically close together, in sorted order by the sort key value.

 
    """


    def __init__(self, AttributeName: str, KeyType: KeyType ):
        "My doc string"
        super().__init__(**{
            "AttributeName": AttributeName,
            "KeyType": KeyType,
        })        




class ProjectionType(str, Enum): 


    ALL = 'ALL'
    
    KEYS_ONLY = 'KEYS_ONLY'
    
    INCLUDE = 'INCLUDE'
    


class Projection(BaseModel):
    """
    Represents attributes that are copied (projected) from the table into an index. These are in addition to the primary key attributes and index key attributes, which are automatically projected.


    """


    ProjectionType: ProjectionType 
    """
    The set of attributes that are projected into the index:

 *  `KEYS_ONLY` - Only the index and primary keys are projected into the index.


*  `INCLUDE` - In addition to the attributes described in `KEYS_ONLY`, the secondary index will include other non-key attributes that you specify.


*  `ALL` - All of the table attributes are projected into the index.



    """

    NonKeyAttributes: List[str]


    def __init__(self, ProjectionType: ProjectionType, NonKeyAttributes: List[str] ):
        "My doc string"
        super().__init__(**{
            "ProjectionType": ProjectionType,
            "NonKeyAttributes": NonKeyAttributes,
        })        



class LocalSecondaryIndex(BaseModel):
    """
    Represents the properties of a local secondary index.


    """


    IndexName: str
    """
    The name of the local secondary index. The name must be unique among all other indexes on this table.


    """

    KeySchema: List[KeySchemaElement]
    """
    Represents *a single element* of a key schema. A key schema specifies the attributes that make up the primary key of a table, or the key attributes of an index.

 A `KeySchemaElement` represents exactly one attribute of the primary key. For example, a simple primary key would be represented by one `KeySchemaElement` (for the partition key). A composite primary key would require one `KeySchemaElement` for the partition key, and another `KeySchemaElement` for the sort key.

 A `KeySchemaElement` must be a scalar, top-level attribute (not a nested attribute). The data type must be one of String, Number, or Binary. The attribute cannot be nested within a List or a Map.


    """

    Projection: Projection 
    """
    Represents attributes that are copied (projected) from the table into the local secondary index. These are in addition to the primary key attributes and index key attributes, which are automatically projected. 


    """


    def __init__(self, IndexName: str, KeySchema: List[KeySchemaElement], Projection: Projection ):
        "My doc string"
        super().__init__(**{
            "IndexName": IndexName,
            "KeySchema": KeySchema,
            "Projection": Projection,
        })        



class ProvisionedThroughput(BaseModel):
    """
    Represents the provisioned throughput settings for a specified table or index. The settings can be modified using the `UpdateTable` operation.

 For current minimum and maximum provisioned throughput values, see [Service, Account, and Table Quotas](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html) in the *Amazon DynamoDB Developer Guide*.


    """


    ReadCapacityUnits: int
    """
    The maximum number of writes consumed per second before DynamoDB returns a `ThrottlingException`. For more information, see [Specifying Read and Write Requirements](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithTables.html#ProvisionedThroughput) in the *Amazon DynamoDB Developer Guide*.

 If read/write capacity mode is `PAY_PER_REQUEST` the value is set to 0.


    """

    WriteCapacityUnits: int
    """
    The maximum number of writes consumed per second before DynamoDB returns a `ThrottlingException`. For more information, see [Specifying Read and Write Requirements](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithTables.html#ProvisionedThroughput) in the *Amazon DynamoDB Developer Guide*.

 If read/write capacity mode is `PAY_PER_REQUEST` the value is set to 0.


    """


    def __init__(self, ReadCapacityUnits: int, WriteCapacityUnits: int ):
        "My doc string"
        super().__init__(**{
            "ReadCapacityUnits": ReadCapacityUnits,
            "WriteCapacityUnits": WriteCapacityUnits,
        })        



class GlobalSecondaryIndex(BaseModel):
    """
    Represents the properties of a global secondary index.


    """


    IndexName: str
    """
    The name of the global secondary index. The name must be unique among all other indexes on this table.


    """

    KeySchema: List[KeySchemaElement]
    """
    Represents *a single element* of a key schema. A key schema specifies the attributes that make up the primary key of a table, or the key attributes of an index.

 A `KeySchemaElement` represents exactly one attribute of the primary key. For example, a simple primary key would be represented by one `KeySchemaElement` (for the partition key). A composite primary key would require one `KeySchemaElement` for the partition key, and another `KeySchemaElement` for the sort key.

 A `KeySchemaElement` must be a scalar, top-level attribute (not a nested attribute). The data type must be one of String, Number, or Binary. The attribute cannot be nested within a List or a Map.


    """

    Projection: Projection 
    """
    Represents attributes that are copied (projected) from the table into the global secondary index. These are in addition to the primary key attributes and index key attributes, which are automatically projected. 


    """

    ProvisionedThroughput: ProvisionedThroughput 
    """
    Represents the provisioned throughput settings for the specified global secondary index.

 For current minimum and maximum provisioned throughput values, see [Service, Account, and Table Quotas](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html) in the *Amazon DynamoDB Developer Guide*.


    """


    def __init__(self, IndexName: str, KeySchema: List[KeySchemaElement], Projection: Projection, ProvisionedThroughput: ProvisionedThroughput ):
        "My doc string"
        super().__init__(**{
            "IndexName": IndexName,
            "KeySchema": KeySchema,
            "Projection": Projection,
            "ProvisionedThroughput": ProvisionedThroughput,
        })        



class BillingMode(str, Enum): 


    PROVISIONED = 'PROVISIONED'
    
    PAY_PER_REQUEST = 'PAY_PER_REQUEST'
    

class StreamViewType(str, Enum): 


    NEW_IMAGE = 'NEW_IMAGE'
    
    OLD_IMAGE = 'OLD_IMAGE'
    
    NEW_AND_OLD_IMAGES = 'NEW_AND_OLD_IMAGES'
    
    KEYS_ONLY = 'KEYS_ONLY'
    

class StreamSpecification(BaseModel):
    """
    Represents the DynamoDB Streams configuration for a table in DynamoDB.


    """


    StreamEnabled: bool
    """
    Indicates whether DynamoDB Streams is enabled (true) or disabled (false) on the table.


    """

    StreamViewType: StreamViewType 
    """
     When an item in the table is modified, `StreamViewType` determines what information is written to the stream for this table. Valid values for `StreamViewType` are:

 *  `KEYS_ONLY` - Only the key attributes of the modified item are written to the stream.


*  `NEW_IMAGE` - The entire item, as it appears after it was modified, is written to the stream.


*  `OLD_IMAGE` - The entire item, as it appeared before it was modified, is written to the stream.


*  `NEW_AND_OLD_IMAGES` - Both the new and the old item images of the item are written to the stream.



    """


    def __init__(self, StreamEnabled: bool, StreamViewType: StreamViewType ):
        "My doc string"
        super().__init__(**{
            "StreamEnabled": StreamEnabled,
            "StreamViewType": StreamViewType,
        })        



class SSEType(str, Enum): 


    AES256 = 'AES256'
    
    KMS = 'KMS'
    


class SSESpecification(BaseModel):
    """
    Represents the settings used to enable server-side encryption.


    """


    Enabled: bool
    """
    Indicates whether server-side encryption is done using an AWS managed CMK or an AWS owned CMK. If enabled (true), server-side encryption type is set to `KMS` and an AWS managed CMK is used (AWS KMS charges apply). If disabled (false) or not specified, server-side encryption is set to AWS owned CMK.


    """

    SSEType: SSEType 
    """
    Server-side encryption type. The only supported value is:

 *  `KMS` - Server-side encryption that uses AWS Key Management Service. The key is stored in your account and is managed by AWS KMS (AWS KMS charges apply).



    """

    KMSMasterKeyId: str
    """
    The AWS KMS customer master key (CMK) that should be used for the AWS KMS encryption. To specify a CMK, use its key ID, Amazon Resource Name (ARN), alias name, or alias ARN. Note that you should only provide this parameter if the key is different from the default DynamoDB customer master key alias/aws/dynamodb.


    """


    def __init__(self, Enabled: bool, SSEType: SSEType, KMSMasterKeyId: str ):
        "My doc string"
        super().__init__(**{
            "Enabled": Enabled,
            "SSEType": SSEType,
            "KMSMasterKeyId": KMSMasterKeyId,
        })        





class Tag(BaseModel):
    """
    Describes a tag. A tag is a key-value pair. You can add up to 50 tags to a single DynamoDB table. 

  AWS-assigned tag names and values are automatically assigned the `aws:` prefix, which the user cannot assign. AWS-assigned tag names do not count towards the tag limit of 50. User-assigned tag names have the prefix `user:` in the Cost Allocation Report. You cannot backdate the application of a tag. 

 For an overview on tagging DynamoDB resources, see [Tagging for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tagging.html) in the *Amazon DynamoDB Developer Guide*.


    """


    Key: str
    """
    The key of the tag. Tag keys are case sensitive. Each DynamoDB table can only have up to one tag with the same key. If you try to add an existing tag (same key), the existing tag value will be updated to the new value. 


    """

    Value: str
    """
    The value of the tag. Tag values are case-sensitive and can be null.


    """


    def __init__(self, Key: str, Value: str ):
        "My doc string"
        super().__init__(**{
            "Key": Key,
            "Value": Value,
        })        



class UpdateGlobalSecondaryIndexAction(BaseModel):
    """
    Represents the new provisioned throughput settings to be applied to a global secondary index.


    """


    IndexName: str
    """
    The name of the global secondary index to be updated.


    """

    ProvisionedThroughput: ProvisionedThroughput 
    """
    Represents the provisioned throughput settings for the specified global secondary index.

 For current minimum and maximum provisioned throughput values, see [Service, Account, and Table Quotas](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html) in the *Amazon DynamoDB Developer Guide*.


    """


    def __init__(self, IndexName: str, ProvisionedThroughput: ProvisionedThroughput ):
        "My doc string"
        super().__init__(**{
            "IndexName": IndexName,
            "ProvisionedThroughput": ProvisionedThroughput,
        })        



class CreateGlobalSecondaryIndexAction(BaseModel):
    """
    Represents a new global secondary index to be added to an existing table.


    """


    IndexName: str
    """
    The name of the global secondary index to be created.


    """

    KeySchema: List[KeySchemaElement]
    """
    Represents *a single element* of a key schema. A key schema specifies the attributes that make up the primary key of a table, or the key attributes of an index.

 A `KeySchemaElement` represents exactly one attribute of the primary key. For example, a simple primary key would be represented by one `KeySchemaElement` (for the partition key). A composite primary key would require one `KeySchemaElement` for the partition key, and another `KeySchemaElement` for the sort key.

 A `KeySchemaElement` must be a scalar, top-level attribute (not a nested attribute). The data type must be one of String, Number, or Binary. The attribute cannot be nested within a List or a Map.


    """

    Projection: Projection 
    """
    Represents attributes that are copied (projected) from the table into an index. These are in addition to the primary key attributes and index key attributes, which are automatically projected.


    """

    ProvisionedThroughput: ProvisionedThroughput 
    """
    Represents the provisioned throughput settings for the specified global secondary index.

 For current minimum and maximum provisioned throughput values, see [Service, Account, and Table Quotas](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html) in the *Amazon DynamoDB Developer Guide*.


    """


    def __init__(self, IndexName: str, KeySchema: List[KeySchemaElement], Projection: Projection, ProvisionedThroughput: ProvisionedThroughput ):
        "My doc string"
        super().__init__(**{
            "IndexName": IndexName,
            "KeySchema": KeySchema,
            "Projection": Projection,
            "ProvisionedThroughput": ProvisionedThroughput,
        })        



class DeleteGlobalSecondaryIndexAction(BaseModel):
    """
    Represents a global secondary index to be deleted from an existing table.


    """


    IndexName: str
    """
    The name of the global secondary index to be deleted.


    """


    def __init__(self, IndexName: str ):
        "My doc string"
        super().__init__(**{
            "IndexName": IndexName,
        })        



class GlobalSecondaryIndexUpdate(BaseModel):
    """
    Represents one of the following:

 * A new global secondary index to be added to an existing table.


* New provisioned throughput parameters for an existing global secondary index.


* An existing global secondary index to be removed from an existing table.



    """


    Update: UpdateGlobalSecondaryIndexAction 
    """
    The name of an existing global secondary index, along with new provisioned throughput settings to be applied to that index.


    """

    Create: CreateGlobalSecondaryIndexAction 
    """
    The parameters required for creating a global secondary index on an existing table:

 *  `IndexName`  


*  `KeySchema`  


*  `AttributeDefinitions`  


*  `Projection`  


*  `ProvisionedThroughput`  



    """

    Delete: DeleteGlobalSecondaryIndexAction 
    """
    The name of an existing global secondary index to be removed.


    """


    def __init__(self, Update: UpdateGlobalSecondaryIndexAction, Create: CreateGlobalSecondaryIndexAction, Delete: DeleteGlobalSecondaryIndexAction ):
        "My doc string"
        super().__init__(**{
            "Update": Update,
            "Create": Create,
            "Delete": Delete,
        })        




class ProvisionedThroughputOverride(BaseModel):
    """
    Replica-specific provisioned throughput settings. If not specified, uses the source table's provisioned throughput settings.


    """


    ReadCapacityUnits: int
    """
    Replica-specific read capacity units. If not specified, uses the source table's read capacity settings.


    """


    def __init__(self, ReadCapacityUnits: int ):
        "My doc string"
        super().__init__(**{
            "ReadCapacityUnits": ReadCapacityUnits,
        })        



class ReplicaGlobalSecondaryIndex(BaseModel):
    """
    Represents the properties of a replica global secondary index.


    """


    IndexName: str
    """
    The name of the global secondary index.


    """

    ProvisionedThroughputOverride: ProvisionedThroughputOverride 
    """
    Replica table GSI-specific provisioned throughput. If not specified, uses the source table GSI's read capacity settings.


    """


    def __init__(self, IndexName: str, ProvisionedThroughputOverride: ProvisionedThroughputOverride ):
        "My doc string"
        super().__init__(**{
            "IndexName": IndexName,
            "ProvisionedThroughputOverride": ProvisionedThroughputOverride,
        })        



class CreateReplicationGroupMemberAction(BaseModel):
    """
    Represents a replica to be created.


    """


    RegionName: str
    """
    The Region where the new replica will be created.


    """

    KMSMasterKeyId: str
    """
    The AWS KMS customer master key (CMK) that should be used for AWS KMS encryption in the new replica. To specify a CMK, use its key ID, Amazon Resource Name (ARN), alias name, or alias ARN. Note that you should only provide this parameter if the key is different from the default DynamoDB KMS master key alias/aws/dynamodb.


    """

    ProvisionedThroughputOverride: ProvisionedThroughputOverride 
    """
    Replica-specific provisioned throughput. If not specified, uses the source table's provisioned throughput settings.


    """

    GlobalSecondaryIndexes: List[ReplicaGlobalSecondaryIndex]
    """
    Represents the properties of a replica global secondary index.


    """


    def __init__(self, RegionName: str, KMSMasterKeyId: str, ProvisionedThroughputOverride: ProvisionedThroughputOverride, GlobalSecondaryIndexes: List[ReplicaGlobalSecondaryIndex] ):
        "My doc string"
        super().__init__(**{
            "RegionName": RegionName,
            "KMSMasterKeyId": KMSMasterKeyId,
            "ProvisionedThroughputOverride": ProvisionedThroughputOverride,
            "GlobalSecondaryIndexes": GlobalSecondaryIndexes,
        })        



class UpdateReplicationGroupMemberAction(BaseModel):
    """
    Represents a replica to be modified.


    """


    RegionName: str
    """
    The Region where the replica exists.


    """

    KMSMasterKeyId: str
    """
    The AWS KMS customer master key (CMK) of the replica that should be used for AWS KMS encryption. To specify a CMK, use its key ID, Amazon Resource Name (ARN), alias name, or alias ARN. Note that you should only provide this parameter if the key is different from the default DynamoDB KMS master key alias/aws/dynamodb.


    """

    ProvisionedThroughputOverride: ProvisionedThroughputOverride 
    """
    Replica-specific provisioned throughput. If not specified, uses the source table's provisioned throughput settings.


    """

    GlobalSecondaryIndexes: List[ReplicaGlobalSecondaryIndex]
    """
    Represents the properties of a replica global secondary index.


    """


    def __init__(self, RegionName: str, KMSMasterKeyId: str, ProvisionedThroughputOverride: ProvisionedThroughputOverride, GlobalSecondaryIndexes: List[ReplicaGlobalSecondaryIndex] ):
        "My doc string"
        super().__init__(**{
            "RegionName": RegionName,
            "KMSMasterKeyId": KMSMasterKeyId,
            "ProvisionedThroughputOverride": ProvisionedThroughputOverride,
            "GlobalSecondaryIndexes": GlobalSecondaryIndexes,
        })        



class DeleteReplicationGroupMemberAction(BaseModel):
    """
    Represents a replica to be deleted.


    """


    RegionName: str
    """
    The Region where the replica exists.


    """


    def __init__(self, RegionName: str ):
        "My doc string"
        super().__init__(**{
            "RegionName": RegionName,
        })        



class ReplicationGroupUpdate(BaseModel):
    """
    Represents one of the following:

 * A new replica to be added to an existing regional table or global table. This request invokes the `CreateTableReplica` action in the destination Region.


* New parameters for an existing replica. This request invokes the `UpdateTable` action in the destination Region.


* An existing replica to be deleted. The request invokes the `DeleteTableReplica` action in the destination Region, deleting the replica and all if its items in the destination Region.



    """


    Create: CreateReplicationGroupMemberAction 
    """
    The parameters required for creating a replica for the table.


    """

    Update: UpdateReplicationGroupMemberAction 
    """
    The parameters required for updating a replica for the table.


    """

    Delete: DeleteReplicationGroupMemberAction 
    """
    The parameters required for deleting a replica for the table.


    """


    def __init__(self, Create: CreateReplicationGroupMemberAction, Update: UpdateReplicationGroupMemberAction, Delete: DeleteReplicationGroupMemberAction ):
        "My doc string"
        super().__init__(**{
            "Create": Create,
            "Update": Update,
            "Delete": Delete,
        })        




class table_output(str, Enum):
    """
    The `CreateTable` operation adds a new table to your account. In an AWS account, table names must be unique within each Region. That is, you can have two tables with same name if you create the tables in different Regions.

  `CreateTable` is an asynchronous operation. Upon receiving a `CreateTable` request, DynamoDB immediately returns a response with a `TableStatus` of `CREATING`. After the table is created, DynamoDB sets the `TableStatus` to `ACTIVE`. You can perform read and write operations only on an `ACTIVE` table. 

 You can optionally define secondary indexes on the new table, as part of the `CreateTable` operation. If you want to create multiple tables with secondary indexes on them, you must create the tables sequentially. Only one table with secondary indexes can be in the `CREATING` state at any given time.

 You can use the `DescribeTable` action to check the table status.


    """

    AttributeDefinitions = "AttributeDefinitions"
    """
    An array of `AttributeDefinition` objects. Each of these objects describes one attribute in the table and index key schema.

 Each `AttributeDefinition` object in this array is composed of:

 *  `AttributeName` - The name of the attribute.


*  `AttributeType` - The data type for the attribute.



    """

    TableName = "TableName"
    """
    The name of the table.


    """

    KeySchema = "KeySchema"
    """
    The primary key structure for the table. Each `KeySchemaElement` consists of:

 *  `AttributeName` - The name of the attribute.


*  `KeyType` - The role of the attribute:


	+  `HASH` - partition key
	
	
	+  `RANGE` - sort key The partition key of an item is also known as its *hash attribute*. The term "hash attribute" derives from DynamoDB's usage of an internal hash function to evenly distribute data items across partitions, based on their partition key values.

 The sort key of an item is also known as its *range attribute*. The term "range attribute" derives from the way DynamoDB stores items with the same partition key physically close together, in sorted order by the sort key value.

 

 For more information about primary keys, see [Primary Key](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DataModel.html#DataModelPrimaryKey) in the *Amazon DynamoDB Developer Guide*.


    """

    TableStatus = "TableStatus"
    """
    The current state of the table:

 *  `CREATING` - The table is being created.


*  `UPDATING` - The table is being updated.


*  `DELETING` - The table is being deleted.


*  `ACTIVE` - The table is ready for use.


*  `INACCESSIBLE_ENCRYPTION_CREDENTIALS` - The AWS KMS key used to encrypt the table in inaccessible. Table operations may fail due to failure to use the AWS KMS key. DynamoDB will initiate the table archival process when a table's AWS KMS key remains inaccessible for more than seven days. 


*  `ARCHIVING` - The table is being archived. Operations are not allowed until archival is complete. 


*  `ARCHIVED` - The table has been archived. See the ArchivalReason for more information. 



    """

    CreationDateTime = "CreationDateTime"
    """
    The date and time when the table was created, in [UNIX epoch time](http://www.epochconverter.com/) format.


    """

    ProvisionedThroughput = "ProvisionedThroughput"
    """
    The provisioned throughput settings for the table, consisting of read and write capacity units, along with data about increases and decreases.


    """

    TableSizeBytes = "TableSizeBytes"
    """
    The total size of the specified table, in bytes. DynamoDB updates this value approximately every six hours. Recent changes might not be reflected in this value.


    """

    ItemCount = "ItemCount"
    """
    The number of items in the specified table. DynamoDB updates this value approximately every six hours. Recent changes might not be reflected in this value.


    """

    TableArn = "TableArn"
    """
    The Amazon Resource Name (ARN) that uniquely identifies the table.


    """

    TableId = "TableId"
    """
    Unique identifier for the table for which the backup was created. 


    """

    BillingModeSummary = "BillingModeSummary"
    """
    Contains the details for the read/write capacity mode.


    """

    LocalSecondaryIndexes = "LocalSecondaryIndexes"
    """
    Represents one or more local secondary indexes on the table. Each index is scoped to a given partition key value. Tables with one or more local secondary indexes are subject to an item collection size limit, where the amount of data within a given item collection cannot exceed 10 GB. Each element is composed of:

 *  `IndexName` - The name of the local secondary index.


*  `KeySchema` - Specifies the complete index key schema. The attribute names in the key schema must be between 1 and 255 characters (inclusive). The key schema must begin with the same partition key as the table.


*  `Projection` - Specifies attributes that are copied (projected) from the table into the index. These are in addition to the primary key attributes and index key attributes, which are automatically projected. Each attribute specification is composed of:


	+  `ProjectionType` - One of the following:
	
	
		-  `KEYS_ONLY` - Only the index and primary keys are projected into the index.
		
		
		-  `INCLUDE` - Only the specified table attributes are projected into the index. The list of projected attributes is in `NonKeyAttributes`.
		
		
		-  `ALL` - All of the table attributes are projected into the index.
	+  `NonKeyAttributes` - A list of one or more non-key attribute names that are projected into the secondary index. The total count of attributes provided in `NonKeyAttributes`, summed across all of the secondary indexes, must not exceed 20. If you project the same attribute into two different indexes, this counts as two distinct attributes when determining the total.
*  `IndexSizeBytes` - Represents the total size of the index, in bytes. DynamoDB updates this value approximately every six hours. Recent changes might not be reflected in this value.


*  `ItemCount` - Represents the number of items in the index. DynamoDB updates this value approximately every six hours. Recent changes might not be reflected in this value.



 If the table is in the `DELETING` state, no information about indexes will be returned.


    """

    GlobalSecondaryIndexes = "GlobalSecondaryIndexes"
    """
    The global secondary indexes, if any, on the table. Each index is scoped to a given partition key value. Each element is composed of:

 *  `Backfilling` - If true, then the index is currently in the backfilling phase. Backfilling occurs only when a new global secondary index is added to the table. It is the process by which DynamoDB populates the new index with data from the table. (This attribute does not appear for indexes that were created during a `CreateTable` operation.) 

  You can delete an index that is being created during the `Backfilling` phase when `IndexStatus` is set to CREATING and `Backfilling` is true. You can't delete the index that is being created when `IndexStatus` is set to CREATING and `Backfilling` is false. (This attribute does not appear for indexes that were created during a `CreateTable` operation.)


*  `IndexName` - The name of the global secondary index.


*  `IndexSizeBytes` - The total size of the global secondary index, in bytes. DynamoDB updates this value approximately every six hours. Recent changes might not be reflected in this value. 


*  `IndexStatus` - The current status of the global secondary index:


	+  `CREATING` - The index is being created.
	
	
	+  `UPDATING` - The index is being updated.
	
	
	+  `DELETING` - The index is being deleted.
	
	
	+  `ACTIVE` - The index is ready for use.
*  `ItemCount` - The number of items in the global secondary index. DynamoDB updates this value approximately every six hours. Recent changes might not be reflected in this value. 


*  `KeySchema` - Specifies the complete index key schema. The attribute names in the key schema must be between 1 and 255 characters (inclusive). The key schema must begin with the same partition key as the table.


*  `Projection` - Specifies attributes that are copied (projected) from the table into the index. These are in addition to the primary key attributes and index key attributes, which are automatically projected. Each attribute specification is composed of:


	+  `ProjectionType` - One of the following:
	
	
		-  `KEYS_ONLY` - Only the index and primary keys are projected into the index.
		
		
		-  `INCLUDE` - In addition to the attributes described in `KEYS_ONLY`, the secondary index will include other non-key attributes that you specify.
		
		
		-  `ALL` - All of the table attributes are projected into the index.
	+  `NonKeyAttributes` - A list of one or more non-key attribute names that are projected into the secondary index. The total count of attributes provided in `NonKeyAttributes`, summed across all of the secondary indexes, must not exceed 20. If you project the same attribute into two different indexes, this counts as two distinct attributes when determining the total.
*  `ProvisionedThroughput` - The provisioned throughput settings for the global secondary index, consisting of read and write capacity units, along with data about increases and decreases. 



 If the table is in the `DELETING` state, no information about indexes will be returned.


    """

    StreamSpecification = "StreamSpecification"
    """
    The current DynamoDB Streams configuration for the table.


    """

    LatestStreamLabel = "LatestStreamLabel"
    """
    A timestamp, in ISO 8601 format, for this stream.

 Note that `LatestStreamLabel` is not a unique identifier for the stream, because it is possible that a stream from another table might have the same timestamp. However, the combination of the following three elements is guaranteed to be unique:

 * AWS customer ID


* Table name


*  `StreamLabel` 



    """

    LatestStreamArn = "LatestStreamArn"
    """
    The Amazon Resource Name (ARN) that uniquely identifies the latest stream for this table.


    """

    GlobalTableVersion = "GlobalTableVersion"
    """
    Represents the version of [global tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html) in use, if the table is replicated across AWS Regions.


    """

    Replicas = "Replicas"
    """
    Represents replicas of the table.


    """

    RestoreSummary = "RestoreSummary"
    """
    Contains details for the restore.


    """

    SSEDescription = "SSEDescription"
    """
    The description of the server-side encryption status on the specified table.


    """

    ArchivalSummary = "ArchivalSummary"
    """
    Contains information about the table archive.


    """



class table_model(Rendered_Resource):
    """

    The `CreateTable` operation adds a new table to your account. In an AWS account, table names must be unique within each Region. That is, you can have two tables with same name if you create the tables in different Regions.

  `CreateTable` is an asynchronous operation. Upon receiving a `CreateTable` request, DynamoDB immediately returns a response with a `TableStatus` of `CREATING`. After the table is created, DynamoDB sets the `TableStatus` to `ACTIVE`. You can perform read and write operations only on an `ACTIVE` table. 

 You can optionally define secondary indexes on the new table, as part of the `CreateTable` operation. If you want to create multiple tables with secondary indexes on them, you must create the tables sequentially. Only one table with secondary indexes can be in the `CREATING` state at any given time.

 You can use the `DescribeTable` action to check the table status.
    
    """


    AttributeDefinitions: List[AttributeDefinition]
    """
    Represents an attribute for describing the key schema for the table and indexes.
    """

    TableName: str
    """
    The name of the table to create.
    """

    KeySchema: List[KeySchemaElement]
    """
    Represents *a single element* of a key schema. A key schema specifies the attributes that make up the primary key of a table, or the key attributes of an index.

 A `KeySchemaElement` represents exactly one attribute of the primary key. For example, a simple primary key would be represented by one `KeySchemaElement` (for the partition key). A composite primary key would require one `KeySchemaElement` for the partition key, and another `KeySchemaElement` for the sort key.

 A `KeySchemaElement` must be a scalar, top-level attribute (not a nested attribute). The data type must be one of String, Number, or Binary. The attribute cannot be nested within a List or a Map.
    """

    LocalSecondaryIndexes: Optional[List[LocalSecondaryIndex]]
    """
    Represents the properties of a local secondary index.
    """

    GlobalSecondaryIndexes: Optional[List[GlobalSecondaryIndex]]
    """
    Represents the properties of a global secondary index.
    """

    BillingMode: Optional[BillingMode] 
    """
    Controls how you are charged for read and write throughput and how you manage capacity. This setting can be changed later.

 *  `PROVISIONED` - We recommend using `PROVISIONED` for predictable workloads. `PROVISIONED` sets the billing mode to [Provisioned Mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html#HowItWorks.ProvisionedThroughput.Manual).


*  `PAY_PER_REQUEST` - We recommend using `PAY_PER_REQUEST` for unpredictable workloads. `PAY_PER_REQUEST` sets the billing mode to [On-Demand Mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html#HowItWorks.OnDemand).
    """

    ProvisionedThroughput: Optional[ProvisionedThroughput] 
    """
    Represents the provisioned throughput settings for a specified table or index. The settings can be modified using the `UpdateTable` operation.

  If you set BillingMode as `PROVISIONED`, you must specify this property. If you set BillingMode as `PAY_PER_REQUEST`, you cannot specify this property.

 For current minimum and maximum provisioned throughput values, see [Service, Account, and Table Quotas](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html) in the *Amazon DynamoDB Developer Guide*.
    """

    StreamSpecification: Optional[StreamSpecification] 
    """
    The settings for DynamoDB Streams on the table. These settings consist of:

 *  `StreamEnabled` - Indicates whether DynamoDB Streams is to be enabled (true) or disabled (false).


*  `StreamViewType` - When an item in the table is modified, `StreamViewType` determines what information is written to the table's stream. Valid values for `StreamViewType` are:


	+  `KEYS_ONLY` - Only the key attributes of the modified item are written to the stream.
	
	
	+  `NEW_IMAGE` - The entire item, as it appears after it was modified, is written to the stream.
	
	
	+  `OLD_IMAGE` - The entire item, as it appeared before it was modified, is written to the stream.
	
	
	+  `NEW_AND_OLD_IMAGES` - Both the new and the old item images of the item are written to the stream.
    """

    SSESpecification: Optional[SSESpecification] 
    """
    Represents the settings used to enable server-side encryption.
    """

    Tags: Optional[List[Tag]]
    """
    Describes a tag. A tag is a key-value pair. You can add up to 50 tags to a single DynamoDB table. 

  AWS-assigned tag names and values are automatically assigned the `aws:` prefix, which the user cannot assign. AWS-assigned tag names do not count towards the tag limit of 50. User-assigned tag names have the prefix `user:` in the Cost Allocation Report. You cannot backdate the application of a tag. 

 For an overview on tagging DynamoDB resources, see [Tagging for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tagging.html) in the *Amazon DynamoDB Developer Guide*.
    """


    def filter_to_create(self) -> dict:
        NEEDED_ATTRIBUTES = set(['AttributeDefinitions', 'TableName', 'KeySchema', 'LocalSecondaryIndexes', 'GlobalSecondaryIndexes', 'BillingMode', 'ProvisionedThroughput', 'StreamSpecification', 'SSESpecification', 'Tags'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self) -> dict:
        NEEDED_ATTRIBUTES = set(['AttributeDefinitions', 'TableName', 'KeySchema', 'LocalSecondaryIndexes', 'GlobalSecondaryIndexes', 'BillingMode', 'ProvisionedThroughput', 'StreamSpecification', 'SSESpecification', 'Tags'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    class Config:
        extra='ignore'


