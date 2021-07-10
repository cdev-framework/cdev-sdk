import typing
from pydantic.main import BaseModel
from enum import Enum
from typing import List


from cdev.constructs import Cdev_Resource
from cdev.models import Rendered_Resource





class dynamo_db_attribute_types(str, Enum):
    N="N"
    S="S"
    B="B"


class dynamo_db_key_type(str, Enum):
    HASH="HASH"
    RANGE="RANGE"


class dynamo_db_attribute_definition(BaseModel):
    AttributeName:str
    AttributeType: dynamo_db_attribute_types


class dynamo_db_key_schema_element(BaseModel):
    AttributeName: str
    KeyType: dynamo_db_key_type

    def __init__(__pydantic_self__, AttributeName: str, KeyType: dynamo_db_key_type ) -> None:
        """
        Object representation of a dynamo db key element
        """
        super().__init__(**{
            "AttributeName": AttributeName,
            "KeyType": KeyType
        })

class dynamo_db_table(Rendered_Resource):
    TableName: str
    AttributeDefinitions: List[dynamo_db_attribute_definition]
    KeySchema: List[dynamo_db_key_schema_element]



class DynamoDBTable(Cdev_Resource):
    def __init__(self,name: str, TableName: str, AttributeDefinitions: List[dynamo_db_attribute_definition], KeySchema: List[dynamo_db_key_schema_element] ) -> None:
        """
        Object representation of an AWS Dynamodb Table
        """
        
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
