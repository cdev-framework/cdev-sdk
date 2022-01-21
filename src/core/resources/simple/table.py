from enum import Enum
from typing import FrozenSet, List
from pydantic import Field

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher
from core.utils.types import ImmutableModel

from .events import Event, event_model, EventTypes
from .iam import Permission

# log = logger.get_cdev_logger(__name__)
class stream_type(str, Enum):
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


class stream_event_model(event_model):
    """
    something

    Arguments:
        original_resource_name: str
        original_resource_type: str
        event_type: EventTypes
        view_type: stream_type
        batch_size: int
    """
    view_type: stream_type
    batch_size: int


class StreamEvent(Event):
    RUUID = "cdev::simple::table"

    def __init__(self, table_name: str, view_type: stream_type, batch_size: int) -> None:
        self.table_name=table_name
        self.view_type=view_type
        self.batch_size=batch_size
        


    def render(self) -> stream_event_model:
        return stream_event_model(
            original_resource_name=self.table_name,
            original_resource_type=self.RUUID,
            event_type=EventTypes.TABLE_STREAM,
            batch_size=self.batch_size,
            view_type=self.view_type.value,
        )



class attribute_type(str, Enum):
    """
    Attributes of a table can be of the values:\n
    S -> String\n
    N -> Number\n
    B -> Binary\n

    These values will be used by the table to do type checks on data for the defined attribute.

    visit https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table for more details
    """

    S = "S"
    N = "N"
    B = "B"


class key_type(str, Enum):
    """
    Type of key for a defined key on a table. Can be values:
    HASH -> Partion Key
    RANGE -> Sort key

    These value will be used by the primary key to determine how the data is stored in the table.
    visit https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey for more details.
    """

    HASH = "HASH"
    RANGE = "RANGE"


class attribute_definition_model(ImmutableModel):
    attribute_name: str 
    attribute_type: attribute_type

    

class AttributeDefinition:
    def __init__(self, name:str, type: attribute_type) -> None:
        self.name = name
        self.type = type


    def render(self) -> attribute_definition_model:
        return attribute_definition_model(
            attribute_name=self.name,
            attribute_type=self.type
        )

class key_definition_model(ImmutableModel):
    attribute_name: str 
    key_type: key_type


class KeyDefinition:
    def __init__(self, name:str, type: key_type) -> None:
        self.name = name
        self.type = type


    def render(self) -> key_definition_model:
        return key_definition_model(
            attribute_name=self.name,
            key_type=self.type
        )


class simple_table_output(str, Enum):
    cloud_id = "cloud_id"
    table_name = "table_name"


class TablePermissions:
    RUUID = "cdev::simple::table"

    def __init__(self, resource_name) -> None:

        self.READ_TABLE = Permission(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:ConditionCheckItem",
            ],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
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
                "dynamodb:DescribeLimits",
            ],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
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
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_STREAM = Permission(
            actions=[
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:ListShards",
                "dynamodb:ListStreams",
            ],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
            resource_suffix="/stream/*",
        )


class simple_table_model(ResourceModel):
    attributes: FrozenSet[attribute_definition_model]
    keys: FrozenSet[key_definition_model]


class Table(Resource):
    RUUID = "cdev::simple::table"

    def __init__(
        self,
        cdev_name: str,
        attributes: List[AttributeDefinition],
        keys: List[KeyDefinition],
        _nonce: str = "",
    ) -> None:
        super().__init__(cdev_name)

        rv = Table.check_attributes_and_keys(attributes, keys)
        if not rv[0]:
            print(rv[1])
            raise Exception
    
        self._nonce = _nonce

        self.attributes = attributes
        self.keys = keys
        self._stream = None

        self.permissions = TablePermissions(cdev_name)

        self.hash = hasher.hash_list([self.attributes, self.keys, self._nonce])

    def render(self) -> simple_table_model:
        return simple_table_model(
            ruuid=self.RUUID,
            name=self.name,
            hash=self.hash,
            attributes=[x.render() for x in self.attributes],
            keys=[x.render() for x in self.keys],
        )

    def create_stream(
        self, view_type: stream_type, batch_size: int = 100
    ) -> StreamEvent:
        if self._stream:
            print(
                f"Already created stream on this table. Use `get_stream()` to get the current stream."
            )
            raise Exception

        event = StreamEvent(
            table_name=self.name,
            view_type=view_type,
            batch_size=batch_size
        )

        self._stream = event
        return event

    def get_stream(self) -> StreamEvent:
        if not self._stream:
            print(
                "Stream has not been created. Create a stream for this table using the `create_stream` function."
            )
            raise Exception

        return self._stream

    def check_attributes_and_keys(
        attributes: List[AttributeDefinition], keys: List[KeyDefinition]
    ) -> bool:
        """
        Check key constraints based on https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
        """
        if len(keys) > 2:
            return (False, "Only two primary keys can be used")

        primary_key = keys[0]

        if not primary_key:
            return (False, "No Hash key provided")

        if not primary_key.type == key_type.HASH:
            return (False, "First key is not Hash key")

        if not primary_key.name in set(
            [x.name for x in attributes]
        ):
            return (
                False,
                f"Hash key 'AttributeName' ({primary_key.name}) not defined in attributes",
            )

        if len(keys) == 1:
            return (True, "")

        range_key = keys[1]

        if not range_key.type == key_type.RANGE:
            return (False, "Second key is not a Range key")

        if not range_key.name in set(
            [x.name for x in attributes]
        ):
            return (
                False,
                f"Range key 'AttributeName' ({range_key.name}) not defined in attributes",
            )

        return (True, "")

    def from_output(self, key: simple_table_output) -> Cloud_Output:
        return super().from_output(key)
