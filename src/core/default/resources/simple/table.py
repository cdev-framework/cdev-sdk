"""Set of constructs for making No SQL DB Tables
"""
from enum import Enum
from typing import Any, FrozenSet, List, Dict

from core.constructs.resource import (
    Resource,
    TaggableResourceModel,
    TaggableMixin,
    update_hash,
    ResourceOutputs,
    PermissionsAvailableMixin,
)
from core.constructs.cloud_output import Cloud_Output_Str, OutputType
from core.constructs.types import cdev_str_model
from core.constructs.models import ImmutableModel, frozendict

from core.default.resources.simple.events import Event, event_model
from core.default.resources.simple.iam import Permission

from core.utils import hasher

RUUID = "cdev::simple::table"


#################
##### Events
#################
# TODO: Add more documentation on the json schema of the events
class stream_type(str, Enum):
    """Type of streams for a table."""

    KEYS_ONLY = "KEYS_ONLY"
    """Only the key attributes of the modified item."""
    NEW_IMAGE = "NEW_IMAGE"
    """The entire item, as it appears after it was modified."""
    OLD_IMAGE = "OLD_IMAGE"
    """The entire item, as it appeared before it was modified."""
    NEW_AND_OLD_IMAGES = "NEW_AND_OLD_IMAGES"
    """Both the new and the old item images of the item."""


class stream_event_model(event_model):
    """Model to represent a stream event

    Args:
        table_name (str): Cdev name of the API this route is apart of
        view_type (stream_type): Type of eventthe stream produces
        batch_size (int): Size of event batches
    """

    table_name: cdev_str_model
    view_type: stream_type
    batch_size: int
    batch_failure: bool


class StreamEvent(Event):
    """Construct for representing the Stream of a `Table`"""

    def __init__(
        self,
        table_name: str,
        view_type: stream_type,
        batch_size: int,
        batch_failure: bool = True,
    ) -> None:
        """
        Args:
            table_name (str): Cdev name of the API this route is apart of
            view_type (stream_type): Type of eventthe stream produces
            batch_size (int): Size of event batches
        """

        self.cdev_table_name = table_name

        self.table_name = Cloud_Output_Str(
            name=table_name, ruuid=RUUID, key="table_name", type=OutputType.RESOURCE
        )

        self.view_type = view_type
        self.batch_size = batch_size
        self.batch_failure = batch_failure

    def hash(self) -> str:
        return hasher.hash_list(
            [self.cdev_table_name, self.view_type, self.batch_size, self.batch_failure]
        )

    def render(self) -> stream_event_model:
        return stream_event_model(
            originating_resource_name=self.cdev_table_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            batch_size=self.batch_size,
            view_type=self.view_type.value,
            table_name=self.table_name.render(),
            batch_failure=self.batch_failure,
        )


#####################
###### Permission
######################
class TablePermissions:
    """Permissions to provide to other resources to access a `Table`"""

    def __init__(self, resource_name: str) -> None:

        self.READ_TABLE = Permission(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:ConditionCheckItem",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permissions to read data from the Table"""

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
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permissions to write data to the Table"""

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
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permissions to read and write data to and from the Table"""

        self.READ_STREAM = Permission(
            actions=[
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:ListShards",
                "dynamodb:ListStreams",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ).join(["", "/stream/*"]),
            effect="Allow",
        )
        """Permissions to receive and process events from the Table Stream"""


##############
##### Output
##############
class TableOutput(ResourceOutputs):
    """Container object for the returned values from the cloud after a `Table` has been deployed."""

    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def table_name(self) -> Cloud_Output_Str:
        """The name of the generated table"""
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="table_name", type=self.OUTPUT_TYPE
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
    """

    S = "S"
    """String"""
    N = "N"
    """Number"""
    B = "B"
    """Binary"""


class key_type(str, Enum):
    """Type of key for a defined key on a table.

    These value will be used by the primary key to determine how the data is stored in the table.
    visit https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey for more details.
    """

    HASH = "HASH"
    """Partion Key"""
    RANGE = "RANGE"
    """Sort key"""


class attribute_definition_model(ImmutableModel):
    """Model representing an attribute of a `Table`

    Args:
        attribute_name (str)
        attribute_type (`attribute_type`)
    """

    attribute_name: str
    attribute_type: attribute_type


class AttributeDefinition:
    """Construct representing an attribute of a `Table`"""

    def __init__(self, name: str, type: attribute_type) -> None:
        """Create an attribute that will be part of a `Table`

        Args:
            name (str): Name of the attribute
            type (attribute_type): Type of value the attribute stores
        """
        self.name = name
        self.type = type

    def render(self) -> attribute_definition_model:
        return attribute_definition_model(
            attribute_name=self.name, attribute_type=self.type
        )


class key_definition_model(ImmutableModel):
    """Model representing a primary key of a `Table`

    Args:
        attribute_name (str)
        key_type (`key_type`)
    """

    attribute_name: str
    key_type: key_type

class secondary_key_model(ImmutableModel):
    """Model representing a `Secondary Key`


    Args:
        index_name (str)
        attribute_name (str))
    """

    index_name: str
    attribute_name: str

class KeyDefinition:
    """Construct representing a primary key of a `Table`"""

    def __init__(self, name: str, type: key_type) -> None:
        """
        Args:
            name (str): Name of the attribute
            type (key_type): Type of value the attribute stores

        Note that the `name` property must match a `name` of a given `AttributeDefinition` on the created
        table.

        The keys on a table will define the optimal way of retrieving data from the `Table`.


        """
        self.name = name
        self.type = type

    def render(self) -> key_definition_model:
        return key_definition_model(attribute_name=self.name, key_type=self.type)

class SecondaryKeyDefinition:
    """Construct representing a primary key of a `Table`"""

    def __init__(self, index_name: str, attribute_name: str) -> None:
        """
        Args:
            name (str): Name of the index
            attribute_name (str): Name of the attribute that will be the secondary key

        Note that the `name` property must match a `name` of a given `AttributeDefinition` on the created
        table.

        The keys on a table will define the optimal way of retrieving data from the `Table`.


        """
        self.index_name = index_name
        self.attribute_name = attribute_name

    def render(self) -> secondary_key_model:
        return secondary_key_model(index_name=self.index_name, attribute_name=self.attribute_name)

class simple_table_model(TaggableResourceModel):
    """Model representing a `Table`

    Args:
        ResourceModel ([type]): [description]
    """

    attributes: FrozenSet[attribute_definition_model]
    keys: FrozenSet[key_definition_model]
    secondary_key: FrozenSet[secondary_key_model]

class Table(PermissionsAvailableMixin, TaggableMixin, Resource):
    """Create a NoSql Table (DynamoDB)"""

    @update_hash
    def __init__(
        self,
        cdev_name: str,
        attributes: List[AttributeDefinition],
        keys: List[KeyDefinition],
        secondary_key: List[SecondaryKeyDefinition] =[],
        nonce: str = "",
        tags: Dict[str, str] = None,
    ) -> None:
        """
        Args:
            cdev_name (str): Name for the resource.
            attributes (List[AttributeDefinition]): List of Attributes on the Table
            keys (List[KeyDefinition]): List of Key Definitions that make up the primary keys
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
            tags (Dict[str, str]): A set of tags to add to the resource


        <a href='https://code.tutsplus.com/tutorials/a-beginners-guide-to-http-and-rest--net-16340'>More information on how to use a DynamoDB Table</a>

        <a href="/docs/examples/table"> Examples on how to use in Cdev Framework</a>

        <a href="https://docs.aws.amazon.com/dynamodb/index.html"> Documentation on Deployed Resource in the Cloud</a>

        <a href="https://aws.amazon.com/dynamodb/pricing/"> Details on pricing</a>
        """
        super().__init__(cdev_name, RUUID, nonce, tags=tags)

        self._attributes = attributes
        self._keys = keys
        self._secondary_keys = secondary_key
        self._stream = None

        self._available_permissions: TablePermissions = TablePermissions(cdev_name)
        self._output = TableOutput(cdev_name)

    @property
    def output(self) -> TableOutput:
        """Output generated by the Cloud when this resource is deployed."""
        return self._output

    @property
    def available_permissions(self) -> TablePermissions:
        """Permissions that can be granted to other resources to access this `Table`"""
        return self._available_permissions

    @property
    def attributes(self) -> List[AttributeDefinition]:
        """Current Attributes"""
        return self._attributes

    @attributes.setter
    @update_hash
    def attributes(self, value: List[AttributeDefinition]):
        self._attributes = value

    @property
    def keys(self) -> List[KeyDefinition]:
        """Current Primary Key Definitions"""
        return self._keys

    @keys.setter
    @update_hash
    def keys(self, value: List[KeyDefinition]) -> None:
        self._keys = value

    @property
    def secondary_key(self) -> List[SecondaryKeyDefinition]:
        """Current Secondary Keys"""
        return self._secondary_keys

    @secondary_key.setter
    @update_hash
    def secondary_key(self, value: List[SecondaryKeyDefinition]):
        self._secondary_keys = value

    def create_stream(
        self, view_type: stream_type, batch_size: int = 100, batch_failure: bool = True
    ) -> StreamEvent:
        """Create a `StreamEvent` for this table

        Args:
            view_type (stream_type): Type of events to process from the stream.
            batch_size (int, optional): Number events to batch into an Event. Defaults to 100.
            batch_failure (bool, optional): If your function fails to process any message from the batch, the entire batch returns to your stream.

        Raises:
            Exception: If this Table already has a Stream, throw exception. Should use `get_stream()`

        Returns:
            StreamEvent: The created `Stream_Event`
        """
        if self._stream:
            raise Exception(
                f"Already created stream on this table. Use `get_stream()` to get the current stream."
            )

        self._stream = StreamEvent(
            table_name=self.name,
            view_type=view_type,
            batch_size=batch_size,
            batch_failure=batch_failure,
        )

        return self._stream

    def get_stream(self) -> StreamEvent:
        """Get the `StreamEvent` for this `Table`

        Raises:
            Exception: If this Table has not created a stream, throw exception

        Returns:
            StreamEvent: The `StreamEvent` for this Table
        """
        if not self._stream:
            raise Exception(
                "Stream has not been created. Create a stream for this table using the `create_stream` function."
            )

        return self._stream

    def _check_attributes_and_keys(self) -> None:
        """
        Check key constraints based on https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.create_table
        """
        key_count = len(self.keys)
        if key_count == 0:
            return

        if key_count > 2:
            raise Exception("Only two primary keys can be used")

        primary_key = self.keys[0]

        if not primary_key:
            raise Exception("No Hash key provided")

        if not primary_key.type == key_type.HASH:
            raise Exception("First key is not Hash key")

        attributes_names = set([x.name for x in self.attributes])
        if primary_key.name not in attributes_names:
            raise Exception(
                f"Hash key 'AttributeName' ({primary_key.name}) not defined in attributes",
            )

        if key_count == 1:
            return

        range_key = self.keys[1]

        if not range_key.type == key_type.RANGE:
            raise Exception("Second key is not a Range key")

        if range_key.name not in attributes_names:
            raise Exception(
                f"Range key 'AttributeName' ({range_key.name}) not defined in attributes",
            )

    def compute_hash(self) -> None:
        self._hash = hasher.hash_list(
            [
                [x.render() for x in self.attributes],
                [x.render() for x in self.keys],
                self.nonce,
                self._get_tags_hash(),
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
            secondary_key=[x.render() for x in self.secondary_key],
            tags=frozendict(self.tags)
        )
