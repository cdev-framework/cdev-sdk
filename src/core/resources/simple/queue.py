from enum import Enum

from core.constructs.resource import Resource, ResourceModel, Cloud_Output, update_hash
from core.utils import hasher

from .events import Event, event_model, EventTypes
from .iam import Permission

RUUID = "cdev::simple::queue"


######################
##### Events
######################
class queue_event_model(event_model):
    """
    something

    Arguments:
        original_resource_name: str
        original_resource_type: str
        event_type: EventTypes
        batch_size: int
        batch_window: int
    """
    batch_size: int
    batch_window: int


class QueueEvent(Event):
    
    def __init__(self, queue_name: str, batch_size: int, batch_window: int) -> None:

        if batch_size > 10000 or batch_size < 0:
            raise Exception

        self.queue_name=queue_name
        self.batch_size=batch_size
        self.batch_window=batch_window


    def render(self) -> queue_event_model:
        return queue_event_model(
            original_resource_name=self.queue_name,
            original_resource_type=RUUID,
            event_type=EventTypes.QUEUE_TRIGGER,
            batch_size=self.batch_size,
            batch_window=self.batch_window,
        )


######################
###### Permission
######################
class QueuePermissions:

    def __init__(self, resource_name) -> None:
        self.READ_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=f"{RUUID}::{resource_name}",
            effect="Allow",
        )

        self.WRITE_QUEUE = Permission(
            actions=[
                "sqs:SendMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=f"{RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_AND_WRITE_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:SendMessage",
            ],
            cloud_id=f"{RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_EVENTS = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=f"{RUUID}::{resource_name}",
            effect="Allow",
        )


######################
##### Output
######################
class simple_queue_output(str, Enum):
    cloud_id = "cloud_id"
    queue_name = "queue_name"


######################
##### Queue
######################
class simple_queue_model(ResourceModel):
    is_fifo: bool


class Queue(Resource):

    @update_hash
    def __init__(self, cdev_name: str, is_fifo: bool = False, nonce: str = "") -> None:
        """
        A simple sqs queue.

        args:
            cdev_name (str): Name of the resource.
            is_fifo (bool, default=False): if this should be a First-in First-out queue (link to difference).
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
        """
        super().__init__(cdev_name, RUUID, nonce)

        self.is_fifo = is_fifo
        self.permissions = QueuePermissions(cdev_name)

    @property
    def is_fifo(self):
        return self._is_fifo

    @is_fifo.setter
    @update_hash
    def is_fifo(self, value: bool):
        self._is_fifo = value

    def create_event_trigger(
        self, batch_size: int = 10, batch_window: int = 5
    ) -> QueueEvent:
    
        # https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-eventsource
        if self.is_fifo and batch_size > 10:
            raise Exception

        event = QueueEvent(
            queue_name=self.name,
            batch_size=batch_size,
            batch_window=batch_window
        )

        return event
        
    def compute_hash(self):
        self._hash = hasher.hash_list([self.is_fifo, self.nonce])
        
    def render(self) -> simple_queue_model:
        return simple_queue_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            is_fifo=self.is_fifo,
        )

    def from_output(self, key: simple_queue_output) -> Cloud_Output:
        return super().from_output(key)
