"""Set of constructs for making message queues

"""
from typing import Any, Dict

from core.constructs.resource import (
    Resource,
    TaggableResourceModel,
    update_hash,
    ResourceOutputs,
    PermissionsAvailableMixin,
    TaggableMixin,
)
from core.constructs.cloud_output import Cloud_Output_Str, OutputType
from core.constructs.types import cdev_str_model
from core.constructs.models import frozendict

from core.default.resources.simple.events import Event, event_model
from core.default.resources.simple.iam import Permission

from core.utils import hasher

RUUID = "cdev::simple::queue"


######################
##### Events
######################
class queue_event_model(event_model):
    """Model representing a message queue event

    Arguments:
        batch_size: int
        batch_window: int
    """

    queue_arn: cdev_str_model
    batch_size: int
    batch_failure: bool


class QueueEvent(Event):
    """Construct representing the Events from the Queue"""

    def __init__(
        self, queue_name: str, batch_size: int, batch_failure: bool = True
    ) -> None:

        if batch_size > 10000 or batch_size < 0:
            raise Exception

        self.cdev_queue_name = queue_name

        self.queue_arn = Cloud_Output_Str(
            name=queue_name, ruuid=RUUID, key="arn", type=OutputType.RESOURCE
        )

        self.batch_size = batch_size
        self.batch_failure = batch_failure

    def render(self) -> queue_event_model:
        return queue_event_model(
            originating_resource_name=self.cdev_queue_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            queue_arn=self.queue_arn.render(),
            batch_size=self.batch_size,
            batch_failure=self.batch_failure,
        )

    def hash(self) -> str:
        return hasher.hash_list(
            [self.cdev_queue_name, self.batch_size, self.batch_failure]
        )


######################
###### Permission
######################
class QueuePermissions:
    def __init__(self, resource_name: str) -> None:
        self.READ_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to poll for messages from the Queue"""

        self.WRITE_QUEUE = Permission(
            actions=[
                "sqs:SendMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to write messages to the Queue"""

        self.READ_AND_WRITE_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:SendMessage",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to read and write messages to and from the Queue"""

        self.READ_EVENTS = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to receive events to and from the Queue"""


######################
##### Output
######################
class QueueOutput(ResourceOutputs):
    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def queue_name(self) -> Cloud_Output_Str:
        """The name of the generated queue"""
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="queue_name", type=self.OUTPUT_TYPE
        )

    @queue_name.setter
    def queue_name(self, value: Any):
        raise Exception


######################
##### Queue
######################
class queue_model(TaggableResourceModel):
    """Model representing a Message Queue"""

    is_fifo: bool
    """Should the Queue guarantee ordering of messages"""


class Queue(PermissionsAvailableMixin, TaggableMixin, Resource):
    """A Message Queue"""

    @update_hash
    def __init__(
        self,
        cdev_name: str,
        is_fifo: bool = False,
        nonce: str = "",
        tags: Dict[str, str] = None,
    ) -> None:
        """
        args:
            cdev_name (str): Name of the resource.
            is_fifo (bool, default=False): If True, the Queue will guarantee ordering of messages.
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
            tags (Dict[str, str]): A set of tags to add to the resource
        """
        super().__init__(cdev_name, RUUID, nonce, tags=tags)

        self.is_fifo = is_fifo
        self.output = QueueOutput(cdev_name)
        self._event = None

        self.available_permissions: QueuePermissions = QueuePermissions(cdev_name)

    @property
    def is_fifo(self) -> bool:
        """Should the Queue guarantee ordering of messages"""
        return self._is_fifo

    @is_fifo.setter
    @update_hash
    def is_fifo(self, value: bool):
        self._is_fifo = value

    def create_event_trigger(
        self, batch_size: int = 10, batch_failure: bool = True
    ) -> QueueEvent:
        """Create an Event for the Queue that other resources can listen to

        Args:
            batch_size (int, optional): Size of message batch. Defaults to 10.
            batch_failure (bool, optional): If your function fails to process any message from the batch, the entire batch returns to your queue.
        Raises:
            Exception: _description_
            Exception: _description_

        Returns:
            QueueEvent
        """
        if self._event:
            raise Exception(
                "Already created stream on this table. Use `get_stream()` to get the current stream."
            )

        # https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-eventsource
        if self.is_fifo and batch_size > 10:
            raise Exception

        event = QueueEvent(
            queue_name=self.name, batch_size=batch_size, batch_failure=batch_failure
        )

        self._event = event

        return event

    def get_event(self) -> QueueEvent:
        """Get the Event for this Queue

        Raises:
            Exception: _description_

        Returns:
            QueueEvent
        """
        if not self._event:
            raise Exception(
                "Queue Event has not been created. Create a stream for this table using the `create_stream` function before calling this function."
            )

        return self._event

    def compute_hash(self) -> None:
        self._hash = hasher.hash_list(
            [
                self.is_fifo,
                self.nonce,
                self._get_tags_hash(),
            ]
        )

    def render(self) -> queue_model:
        return queue_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            is_fifo=self.is_fifo,
            tags=frozendict(self.tags)
        )
