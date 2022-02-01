from enum import Enum
from typing import Any, FrozenSet, List

from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs, PermissionsAvailableMixin
from core.constructs.output import  Cloud_Output_Str, OutputType
from core.utils import hasher
from core.constructs.models import ImmutableModel

from core.default.resources.simple.events import Event, event_model
from core.default.resources.simple.iam import Permission

RUUID = "cdev::simple::table"


#################
##### Events
#################
class stream_type(str, Enum):
    """Type of streams for a table. 
    
    attributes:
        KEYS_ONLY: Only the key attributes of the modified item.
        NEW_IMAGE: The entire item, as it appears after it was modified.
        OLD_IMAGE: The entire item, as it appeared before it was modified.
        NEW_AND_OLD_IMAGES: Both the new and the old item images of the item.
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
            batch_size=self.batch_size,
            view_type=self.view_type.value,
            granting_permission=TablePermissions(self.table_name).READ_STREAM.render()
        )


#####################
###### Permission
######################
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
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
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
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
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
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
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
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
            effect="Allow",
        )

##############
##### Output
##############
class TableOutput(ResourceOutputs):
    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def table_name(self) -> Cloud_Output_Str:
        """The name of the generated table"""
        return Cloud_Output_Str(
            name=self._name,
            ruuid=RUUID,
            key='table_name',
            type=self.OUTPUT_TYPE
        )

    @table_name.setter
    def table_name(self, value: Any):
        raise Exception


###############
##### Table
###############
class attribute_type(str, Enum):
    """Attributes of a table.

    These values will be used by the table to do type checks on data for the defined attribute.

    visit https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table for more details

    Values:
        S: String
        N: Number
        B: Binary
    """

    S = "S"
    N = "N"
    B = "B"


class key_type(str, Enum):
    """Type of key for a defined key on a table.
    
    These value will be used by the primary key to determine how the data is stored in the table.
    visit https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey for more details.

    Values:
        HASH: Partion Key
        RANGE: Sort key
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


class simple_table_model(ResourceModel):
    attributes: FrozenSet[attribute_definition_model]
    keys: FrozenSet[key_definition_model]


class Table(PermissionsAvailableMixin, Resource):

    @update_hash
    def __init__(
        self,
        cdev_name: str,
        attributes: List[AttributeDefinition],
        keys: List[KeyDefinition],
        nonce: str = "",
    ) -> None:
        """[summary]

        Args:
            cdev_name (str): [description]
            attributes (List[AttributeDefinition]): [description]
            keys (List[KeyDefinition]): [description]
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
        """
        super().__init__(cdev_name, RUUID, nonce)

        self._attributes = attributes
        self._keys = keys
        self._stream = None

        self.available_permissions = TablePermissions(cdev_name)

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    @update_hash
    def attributes(self, value: List[AttributeDefinition]):
        self._attributes = value

    @property
    def keys(self):
        return self._keys

    @keys.setter
    @update_hash
    def keys(self, value: List[KeyDefinition]):
        self._keys = value

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


    def _check_attributes_and_keys(
        self
    ) -> None:
        """
        Check key constraints based on https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
        """
        if len(self.keys) > 2:
            raise Exception("Only two primary keys can be used")

        primary_key = self.keys[0]

        if not primary_key:
            raise Exception("No Hash key provided")

        if not primary_key.type == key_type.HASH:
            raise Exception("First key is not Hash key")

        if not primary_key.name in set(
            [x.name for x in self.attributes]
        ):
            raise Exception(
                f"Hash key 'AttributeName' ({primary_key.name}) not defined in attributes",
            )

        if len(self.keys) == 1:
            return 

        range_key = self.keys[1]

        if not range_key.type == key_type.RANGE:
            raise Exception("Second key is not a Range key")

        if not range_key.name in set(
            [x.name for x in self.attributes]
        ):
            raise Exception(
                f"Range key 'AttributeName' ({range_key.name}) not defined in attributes",
            )

    def compute_hash(self):
        self._hash = hasher.hash_list(
            [
                [x.render() for x in self.attributes], 
                [x.render() for x in self.keys], 
                self.nonce
            ]
        )

    def render(self) -> simple_table_model:
        self._check_attributes_and_keys()
        
        return simple_table_model(
            ruuid=RUUID,
            name=self.name,
            hash=self.hash,
            attributes=[x.render() for x in self.attributes],
            keys=[x.render() for x in self.keys],
        )
