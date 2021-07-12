import typing
from pydantic.main import BaseModel
from enum import Enum
from typing import List


from cdev.constructs import Cdev_Resource
from cdev.models import Rendered_Resource





class dynamo_db_attribute_types(str, Enum):
    """
    (Link to aws documentation)
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
    (Link to aws documentation)

    These are the two key types that are available through Dynamodb. Using a Hash key means that records will be identified by that
    key in generally O(1) time. A range key is used to keep an index that allows for reconstructions of ranges of values
    """

    HASH="HASH"
    RANGE="RANGE"


class dynamo_db_attribute_definition(BaseModel):
    AttributeName: str
    AttributeType: dynamo_db_attribute_types

    def __init__(__pydantic_self__, AttributeName: str, AttributeType: dynamo_db_attribute_types) -> None:
        super().__init__(**{
            "AttributeName": AttributeName,
            "AttributeType": AttributeType
        })


class dynamo_db_key_schema_element(BaseModel):
    """
    (link to aws documentation)

    Object representation of a dynamo db key element
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
            "hash": 1,
            "TableName": TableName,
            "AttributeDefinitions": AttributeDefinitions,
            "KeySchema": KeySchema
        })



class DynamoDBTable(Cdev_Resource):
    """
    Python class for an Aws Dynamodb table

    Attributes:
        name: cdev name for this resource
        TableName: Name the table will receive in AWS
        AttributeDefinitions: List of attributes this Table will have
        KeySchema: The List of key schema that will be used for this table


    """
    def __init__(self,name: str, TableName: str, AttributeDefinitions: List[dynamo_db_attribute_definition], KeySchema: List[dynamo_db_key_schema_element] ) -> None:

        
        super().__init__()
        self.name = name
        self.TableName = TableName
        self.AttributeDefinitions = AttributeDefinitions
        self.KeySchema = KeySchema

    def render(self):
        return dynamo_db_table(**{
            "ruuid": "cdev::aws::dynamodb",
            "name": self.name,
            "hash": 1,
            "TableName": self.TableName,
            "AttributeDefinitions": self.AttributeDefinitions,
            "KeySchema": self.KeySchema
        })
