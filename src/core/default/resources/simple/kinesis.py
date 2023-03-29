"""Set of constructs for making data streams

"""
from enum import Enum
from typing import Any, Dict, Optional

from core.constructs.models import frozendict
from core.constructs.resource import (
    Resource,
    TaggableResourceModel,
    update_hash,
    ResourceOutputs,
    PermissionsAvailableMixin,
    TaggableMixin,
)
from core.constructs.cloud_output import (
    Cloud_Output_Str,
    OutputType,
)
from core.constructs.models import frozendict
from core.constructs.types import cdev_str_model

from core.default.resources.simple.events import Event, event_model
from core.default.resources.simple.iam import Permission

from core.utils import hasher

RUUID = "cdev::simple::data-stream"

######################
###### Permission
######################
class DataStreamPermissions:
    def __init__(self, resource_name: str) -> None:
        self.READ_STREAM = Permission(
            actions=[
                "kinesis:Get*",
                "kinesis:List*",
                "kinesis:Describe*",
                "kinesis:SubscribeToShard",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to poll for messages from the Stream"""

        self.WRITE_STREAM = Permission(
            actions=[
                "kinesis:PutRecord*",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to write messages to the Stream"""

        self.READ_AND_WRITE_STREAM = Permission(
            actions=[
                "kinesis:Get*",
                "kinesis:List*",
                "kinesis:Describe*",
                "kinesis:SubscribeToShard",
                "kinesis:PutRecord*",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to read and write messages to and from the Stream"""


######################
##### Output
######################
class DataStreamOutput(ResourceOutputs):
    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def data_stream_name(self) -> Cloud_Output_Str:
        """The name of the generated data stream"""
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="data_stream_name", type=self.OUTPUT_TYPE
        )

    @data_stream_name.setter
    def set_data_stream_name(self, value: Any):
        raise Exception


########################
##### Consumer
########################
class ConsumerStartingPosition(str, Enum):
    latest = "LATEST"
    trim_horizon = "TRIM_HORIZON"
    at_timestamp = "AT_TIMESTAMP"


class consumer_event_model(event_model):
    """Model to represent an event for a given route"""

    data_stream_arn: cdev_str_model
    batch_size: int
    batch_window: int
    batch_failure: bool
    starting_position: ConsumerStartingPosition
    failure_destination: Optional[str]
    retry_attempts: int
    maximum_record_age: int
    split_batch_on_error: bool
    concurrent_batches_per_shard: int


class ConsumerEvent(Event):
    """Construct for representing a data stream consumer event."""

    def __init__(
        self,
        data_stream_name: str,
        batch_size: int = 100,
        batch_window: int = 0,
        batch_failure: bool = True,
        starting_position: ConsumerStartingPosition = ConsumerStartingPosition.latest,
        failure_destination: str = None,
        retry_attempts: int = 3,
        maximum_record_age: int = 2,
        split_batch_on_error: bool = False,
        concurrent_batches_per_shard: int = 1,
    ) -> None:
        self.data_stream_name = data_stream_name
        self.batch_size = batch_size
        self.batch_window = batch_window
        self.batch_failure = batch_failure
        self.starting_position = starting_position
        self.failure_destination = failure_destination
        self.retry_attempts = retry_attempts
        self.maximum_record_age = maximum_record_age
        self.split_batch_on_error = split_batch_on_error
        self.concurrent_batches_per_shard = concurrent_batches_per_shard

        self.data_stream_arn = Cloud_Output_Str(
            name=data_stream_name, ruuid=RUUID, key="arn", type=OutputType.RESOURCE
        )

    def hash(self) -> str:
        return hasher.hash_list(
            [
                self.batch_size,
                self.batch_window,
                self.starting_position,
                self.failure_destination,
                self.retry_attempts,
                self.maximum_record_age,
                self.split_batch_on_error,
                self.concurrent_batches_per_shard,
            ]
        )

    def render(self) -> consumer_event_model:
        return consumer_event_model(
            originating_resource_name=self.data_stream_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            data_stream_arn=self.data_stream_arn.render(),
            batch_size=self.batch_size,
            batch_window=self.batch_window,
            batch_failure=self.batch_failure,
            starting_position=self.starting_position,
            failure_destination=self.failure_destination,
            retry_attempts=self.retry_attempts,
            maximum_record_age=self.maximum_record_age,
            split_batch_on_error=self.split_batch_on_error,
            concurrent_batches_per_shard=self.concurrent_batches_per_shard,
        )


######################
##### Data Stream
######################
class StreamMode(str, Enum):
    PROVISIONED = "PROVISIONED"
    ON_DEMAND = "ON_DEMAND"


class data_stream_model(TaggableResourceModel):
    """Model representing a Message Queue"""

    stream_mode: StreamMode

    shard_count: Optional[int]


class DataStream(PermissionsAvailableMixin, TaggableMixin, Resource):
    """A Message Queue"""

    @update_hash
    def __init__(
        self,
        cdev_name: str,
        stream_mode: StreamMode,
        shard_count: int = None,
        nonce: str = "",
        tags: Dict[str, str] = None,
    ) -> None:
        """
        args:
            cdev_name (str): Name of the resource.
            stream_mode (StreamMode): 'PROVISIONED'|'ON_DEMAND'
            shard_count (int): Amount of shard to provision if stream_mode is PROVISIONED
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
            tags (Dict[str, str]): A set of tags to add to the resource
        """
        super().__init__(cdev_name, RUUID, nonce, tags=tags)

        if stream_mode == StreamMode.ON_DEMAND and shard_count:
            raise Exception("Can not provide shard_count and ON_DEMAND as stream mode")

        if stream_mode == StreamMode.PROVISIONED and not shard_count:
            raise Exception("Must provide shard_count when stream mode is PROVISIONED")

        self.stream_mode = stream_mode
        self.shard_count = shard_count

        self.output = DataStreamOutput(cdev_name)
        self._event = None

        self.available_permissions: DataStreamPermissions = DataStreamPermissions(
            cdev_name
        )

    def create_event_trigger(
        self,
        batch_size: int = 10,
        batch_window: int = 1,
        batch_failure: bool = True,
        starting_position: ConsumerStartingPosition = ConsumerStartingPosition.latest,
        failure_destination: str = None,
        retry_attempts: int = 3,
        maximum_record_age: int = 60,
        split_batch_on_error: bool = False,
        concurrent_batches_per_shard: int = 1,
    ) -> ConsumerEvent:
        """Create an Event for the Data Stream that other resources can subscribe to"""

        event = ConsumerEvent(
            data_stream_name=self.name,
            batch_size=batch_size,
            batch_window=batch_window,
            batch_failure=batch_failure,
            starting_position=starting_position,
            failure_destination=failure_destination,
            retry_attempts=retry_attempts,
            maximum_record_age=maximum_record_age,
            split_batch_on_error=split_batch_on_error,
            concurrent_batches_per_shard=concurrent_batches_per_shard,
        )
        self._event = event

        return event

    def get_event(self) -> ConsumerEvent:
        """Get the Consumer Event for this Data Stream

        Raises:
            Exception: _description_

        Returns:
            Consumer Event
        """
        if not self._event:
            raise Exception(
                "Consumer Event has not been created. Create a event for this table using the `create_event_trigger` function before calling this function."
            )

        return self._event

    def compute_hash(self) -> None:
        self._hash = hasher.hash_list(
            [
                self.shard_count,
                self.stream_mode,
                self.nonce,
                self._get_tags_hash(),
            ]
        )

    def render(self) -> data_stream_model:
        return data_stream_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            stream_mode=self.stream_mode,
            shard_count=self.shard_count,
            tags=frozendict(self.tags),
        )
