from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .dynamodb_models import *


class Table(Cdev_Resource):
    """
    The `CreateTable` operation adds a new table to your account. In an AWS account, table names must be unique within each Region. That is, you can have two tables with same name if you create the tables in different Regions.

  `CreateTable` is an asynchronous operation. Upon receiving a `CreateTable` request, DynamoDB immediately returns a response with a `TableStatus` of `CREATING`. After the table is created, DynamoDB sets the `TableStatus` to `ACTIVE`. You can perform read and write operations only on an `ACTIVE` table. 

 You can optionally define secondary indexes on the new table, as part of the `CreateTable` operation. If you want to create multiple tables with secondary indexes on them, you must create the tables sequentially. Only one table with secondary indexes can be in the `CREATING` state at any given time.

 You can use the `DescribeTable` action to check the table status.


    """

    def __init__(self,name: str, AttributeDefinitions: List[AttributeDefinition], TableName: str, KeySchema: List[KeySchemaElement], LocalSecondaryIndexes: List[LocalSecondaryIndex]=None, GlobalSecondaryIndexes: List[GlobalSecondaryIndex]=None, BillingMode: BillingMode=None, ProvisionedThroughput: ProvisionedThroughput=None, StreamSpecification: StreamSpecification=None, SSESpecification: SSESpecification=None, Tags: List[Tag]=None):
        ""
        super().__init__(name)

        self.AttributeDefinitions = AttributeDefinitions
        """
        Represents an attribute for describing the key schema for the table and indexes.


        """

        self.TableName = TableName
        """
        The name of the table to create.


        """

        self.KeySchema = KeySchema
        """
        Represents *a single element* of a key schema. A key schema specifies the attributes that make up the primary key of a table, or the key attributes of an index.

 A `KeySchemaElement` represents exactly one attribute of the primary key. For example, a simple primary key would be represented by one `KeySchemaElement` (for the partition key). A composite primary key would require one `KeySchemaElement` for the partition key, and another `KeySchemaElement` for the sort key.

 A `KeySchemaElement` must be a scalar, top-level attribute (not a nested attribute). The data type must be one of String, Number, or Binary. The attribute cannot be nested within a List or a Map.


        """

        self.LocalSecondaryIndexes = LocalSecondaryIndexes
        """
        Represents the properties of a local secondary index.


        """

        self.GlobalSecondaryIndexes = GlobalSecondaryIndexes
        """
        Represents the properties of a global secondary index.


        """

        self.BillingMode = BillingMode
        """
        Controls how you are charged for read and write throughput and how you manage capacity. This setting can be changed later.

 *  `PROVISIONED` - We recommend using `PROVISIONED` for predictable workloads. `PROVISIONED` sets the billing mode to [Provisioned Mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html#HowItWorks.ProvisionedThroughput.Manual).


*  `PAY_PER_REQUEST` - We recommend using `PAY_PER_REQUEST` for unpredictable workloads. `PAY_PER_REQUEST` sets the billing mode to [On-Demand Mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html#HowItWorks.OnDemand). 



        """

        self.ProvisionedThroughput = ProvisionedThroughput
        """
        Represents the provisioned throughput settings for a specified table or index. The settings can be modified using the `UpdateTable` operation.

  If you set BillingMode as `PROVISIONED`, you must specify this property. If you set BillingMode as `PAY_PER_REQUEST`, you cannot specify this property.

 For current minimum and maximum provisioned throughput values, see [Service, Account, and Table Quotas](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Limits.html) in the *Amazon DynamoDB Developer Guide*.


        """

        self.StreamSpecification = StreamSpecification
        """
        The settings for DynamoDB Streams on the table. These settings consist of:

 *  `StreamEnabled` - Indicates whether DynamoDB Streams is to be enabled (true) or disabled (false).


*  `StreamViewType` - When an item in the table is modified, `StreamViewType` determines what information is written to the table's stream. Valid values for `StreamViewType` are:


	+  `KEYS_ONLY` - Only the key attributes of the modified item are written to the stream.
	
	
	+  `NEW_IMAGE` - The entire item, as it appears after it was modified, is written to the stream.
	
	
	+  `OLD_IMAGE` - The entire item, as it appeared before it was modified, is written to the stream.
	
	
	+  `NEW_AND_OLD_IMAGES` - Both the new and the old item images of the item are written to the stream.

        """

        self.SSESpecification = SSESpecification
        """
        Represents the settings used to enable server-side encryption.


        """

        self.Tags = Tags
        """
        Describes a tag. A tag is a key-value pair. You can add up to 50 tags to a single DynamoDB table. 

  AWS-assigned tag names and values are automatically assigned the `aws:` prefix, which the user cannot assign. AWS-assigned tag names do not count towards the tag limit of 50. User-assigned tag names have the prefix `user:` in the Cost Allocation Report. You cannot backdate the application of a tag. 

 For an overview on tagging DynamoDB resources, see [Tagging for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tagging.html) in the *Amazon DynamoDB Developer Guide*.


        """

        self.hash = hasher.hash_list([self.AttributeDefinitions, self.TableName, self.KeySchema, self.LocalSecondaryIndexes, self.GlobalSecondaryIndexes, self.BillingMode, self.ProvisionedThroughput, self.StreamSpecification, self.SSESpecification, self.Tags])

    def render(self) -> table_model:
        data = {
            "ruuid": "cdev::aws::dynamodb::table",
            "name": self.name,
            "hash": self.hash,
            "AttributeDefinitions": self.AttributeDefinitions,
            "TableName": self.TableName,
            "KeySchema": self.KeySchema,
            "LocalSecondaryIndexes": self.LocalSecondaryIndexes,
            "GlobalSecondaryIndexes": self.GlobalSecondaryIndexes,
            "BillingMode": self.BillingMode,
            "ProvisionedThroughput": self.ProvisionedThroughput,
            "StreamSpecification": self.StreamSpecification,
            "SSESpecification": self.SSESpecification,
            "Tags": self.Tags,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return table_model(**filtered_data)

    def from_output(self, key: table_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::aws::dynamodb::table::{self.hash}", "key": key})


