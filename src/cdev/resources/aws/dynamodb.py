import typing
from pydantic.main import BaseModel
from enum import Enum
from typing import List


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher





class dynamo_db_attribute_types(str, Enum):
    """
    [AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table)

    A dynamo db attribute type is used to denote the data type the a dynamodb key will be associated with. 

    - N: Number
    - S: String
    - B: Binary
    """

    N="N"
    S="S"
    B="B"


class dynamo_db_key_type(str, Enum):
    """
    [AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table)

    These are the two key types that are available through Dynamodb. Using a Hash key means that records will be identified by that
    key in generally O(1) time. A range key is used to keep an index that allows for reconstructions of ranges of values
    """

    HASH="HASH"
    RANGE="RANGE"


class dynamo_db_attribute_definition(BaseModel):
    """
    [AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table)
    
    
    Attribute that describe the key schema for the table and indexes.
    """

    AttributeName: str
    AttributeType: dynamo_db_attribute_types

    def __init__(__pydantic_self__, AttributeName: str, AttributeType: dynamo_db_attribute_types) -> None:
        super().__init__(**{
            "AttributeName": AttributeName,
            "AttributeType": AttributeType
        })


class dynamo_db_key_schema_element(BaseModel):
    """
    [AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table)
    """

    
    AttributeName: str
    KeyType: dynamo_db_key_type

    def __init__(__pydantic_self__, AttributeName: str, KeyType: dynamo_db_key_type ) -> None:

        super().__init__(**{
            "AttributeName": AttributeName,
            "KeyType": KeyType
        })


class dynamo_db_table(Rendered_Resource):
    """
    [AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table)

    High level representation of a Dynamodb table that is stored in Cdev's memory. This should be constructed from the `render`
    method of a DynamoDBTable.

    Attributes:
        TableName: Name of the table
        AttributeDefinition: 
    """
    TableName: str
    AttributeDefinitions: List[dynamo_db_attribute_definition]
    KeySchema: List[dynamo_db_key_schema_element]

    def __init__(__pydantic_self__, name: str, ruuid: str, hash:str, TableName: str, AttributeDefinitions: List[dynamo_db_attribute_definition], KeySchema: List[dynamo_db_key_schema_element] ) -> None:
        super().__init__(**{
            "ruuid": ruuid,
            "name": name,
            "hash": hash,
            "TableName": TableName,
            "AttributeDefinitions": AttributeDefinitions,
            "KeySchema": KeySchema
        })




class DynamoDBTable_Output(str, Enum):
    TableArn = "TableArn"
    TableName = "TableName"


class DynamoDBTable(Cdev_Resource):
    """
    
    [AWS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table)

    Python class for an Aws Dynamodb table

    The attributes in KeySchema must also be defined in the AttributeDefinitions List. If the Attribute isn't present in the AttributeDefinitions 
    List, this object will throw an error.
    TODO throw error

    More information about the [DynamoDB Data Model](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.html)

    Attributes:
        name: cdev name for this resource
        TableName: Name the table will receive in AWS
        AttributeDefinitions: List of attributes this Table will have
        KeySchema: The List of key schema that will be used for this table
    """

    OUTPUTS = set([""])


    def __init__(self,name: str, TableName: str, AttributeDefinitions: List[dynamo_db_attribute_definition], KeySchema: List[dynamo_db_key_schema_element] ) -> None:

        
        super().__init__(name)
        self.TableName = TableName
        self.AttributeDefinitions = AttributeDefinitions
        self.KeySchema = KeySchema
        self.hash = hasher.hash_string(self.TableName)

    def render(self):
        return dynamo_db_table(**{
            "ruuid": "cdev::aws::dynamodb",
            "name": self.name,
            "hash": self.hash,
            "TableName": self.TableName,
            "AttributeDefinitions": self.AttributeDefinitions,
            "KeySchema": self.KeySchema
        })

    def from_output(self, key: DynamoDBTable_Output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::aws::dynamodb::{self.hash}", "key": key})
