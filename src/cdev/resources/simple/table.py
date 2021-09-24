from enum import Enum
from os import supports_effective_ids
from typing import List, Dict, Union


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher, environment as cdev_environment

from .xlambda import Event as lambda_event, EventTypes, Permission

#log = logger.get_cdev_logger(__name__)




class attribute_type(Enum):
    """
    Attributes of a table can be of the values:\n
    S -> String\n
    N -> Number\n
    B -> Binary\n

    These values will be used by the table to do type checks on data for the defined attribute.

    visit https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table for more details
    """
    S="S" 
    N="N" 
    B="B"


class key_type(Enum):
    """
    Type of key for a defined key on a table. Can be values:
    HASH -> Partion Key
    RANGE -> Sort key

    These value will be used by the primary key to determine how the data is stored in the table.
    visit https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey for more details.
    """

    HASH = "HASH"
    RANGE = "RANGE"


class stream_type(Enum):
    """
    Type of streams for a table. Can be values:\n
    KEYS_ONLY -> Only the key attributes of the modified item.\n
    NEW_IMAGE -> The entire item, as it appears after it was modified.\n
    OLD_IMAGE -> The entire item, as it appeared before it was modified.\n
    NEW_AND_OLD_IMAGES -> Both the new and the old item images of the item.\n
    """
    KEYS_ONLY = "KEYS_ONLY"
    NEW_IMAGE = "NEW_IMAGE"
    OLD_IMAGE = "OLD_IMAGE"
    NEW_AND_OLD_IMAGES = "NEW_AND_OLD_IMAGES"


class simple_table_model(Rendered_Resource):
    table_name: str
    attributes: List[Dict[str, str]]
    keys: List[Dict[str,  str]]


class simple_table_output(str, Enum):
    cloud_id = "cloud_id"
    table_name = "table_name"


class TablePermissions():

    def __init__(self, resource_name) -> None:
    
        self.READ_TABLE = Permission(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:ConditionCheckItem"
            ],
            resource=f'cdev::simple::table::{resource_name}',
            effect="Allow"
        )
    
        self.WRITE_TABLE = Permission(
            actions=[
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:ConditionCheckItem",
                "dynamodb:PutItem",
                "dynamodb:DescribeTable",
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:UpdateItem",
                "dynamodb:DescribeLimits"
            ],
            resource=f'cdev::simple::table::{resource_name}',
            effect="Allow"
        )
    
        self.READ_AND_WRITE_TABLE = Permission(
            actions=[   
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:ConditionCheckItem",
                "dynamodb:DeleteItem",
                "dynamodb:DescribeLimits",
                "dynamodb:DescribeTable",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
            ],
            resource=f'cdev::simple::table::{resource_name}',
            effect="Allow"
        )
    
        self.READ_STREAM = Permission(
            actions=[
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:ListShards",
                "dynamodb:ListStreams"
            ],
            resource=f'cdev::simple::table::{resource_name}',
            effect="Allow",
            resource_suffix="/stream/*"
        )


class Table(Cdev_Resource):
    def __init__(self, cdev_name: str, attributes: List[Dict[str, Union[attribute_type,str]]], keys: List[Dict[str, Union[key_type, str]]], table_name: str="") -> None:
        rv = Table.check_attributes_and_keys(attributes, keys)
        if not rv[0]:
            print(rv[1])
            raise Exception

        super().__init__(cdev_name)



        self.table_name = f"{table_name}_{cdev_environment.get_current_environment_hash()}" if table_name else f"{cdev_name}_{cdev_environment.get_current_environment_hash()}"
        self.attributes = [{"AttributeName": x.get("AttributeName"), "AttributeType": x.get("AttributeType").value} for x in attributes]
        self.keys = [{"AttributeName": x.get("AttributeName"), "KeyType": x.get("KeyType").value} for x in keys]
        self._stream = None

        self.permissions = TablePermissions(cdev_name)

        self.hash = hasher.hash_list([self.table_name, self.attributes, self.keys])

    def render(self) -> simple_table_model:
        return simple_table_model(**{
            "ruuid": "cdev::simple::table",
            "name": self.name,
            "hash": self.hash ,
            "table_name": self.table_name,
            "attributes": self.attributes,
            "keys": self.keys
            }
        )

    def create_stream(self, view_type: stream_type, batch_size: int = 100) -> lambda_event:
        if self._stream:
            print(f"Already created stream on this table. Use `get_stream()` to get the current stream.")
            raise Exception


        config = {
            "ViewType": view_type.value,
            "BatchSize": batch_size
        }


        event = lambda_event(**{
            "original_resource_name": self.name,
            "original_resource_type": "cdev::simple::table",
            "event_type": EventTypes.TABLE_STREAM,
            "config": config
            }
        )

        self._stream = event
        return event


    def get_stream(self) -> lambda_event:
        if not self._stream:
            print("Stream has not been created. Create a stream for this table using the `create_stream` function.")
            raise Exception

        return self._stream

    def check_attributes_and_keys(attributes: List[Dict[str, attribute_type]], keys: List[Dict[str, key_type]]) -> bool:
        """
        Check key constraints based on https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
        """
        if len(keys) > 2:
            return (False, "Only two primary keys can be used")


        primary_key = keys[0]


        if not primary_key:
            return (False, "No Hash key provided")

        if not primary_key.get("KeyType") == key_type.HASH:
            return (False, "First key is not Hash key")

        if not primary_key.get("AttributeName") in set([x.get("AttributeName") for x in attributes]):
            return (False, f"Hash key 'AttributeName' ({primary_key.get('AttributeName')}) not defined in attributes")

        if len(keys) == 1:
            return (True, "")

        range_key = keys[1]

        if not range_key.get("KeyType") == key_type.RANGE:
            return (False, "FSecond key is not a Range key")

        if not range_key.get("AttributeName") in set([x.get("AttributeName") for x in attributes]):
            return (False, f"Range key 'AttributeName' ({range_key.get('AttributeName')}) not defined in attributes")


        
        return (True,"")

    def from_output(self, key: simple_table_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::simple::table::{self.hash}", "key": key.value, "type": "cdev_output"})


