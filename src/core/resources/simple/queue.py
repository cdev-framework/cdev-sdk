from enum import Enum
from typing import List, Dict, Union

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher


from .events import Event, event_model, EventTypes
from .iam import Permission



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
    RUUID = "cdev::simple::queue"

    def __init__(self, queue_name: str, batch_size: int, batch_window: int) -> None:

        if batch_size > 10000 or batch_size < 0:
            raise Exception

        self.queue_name=queue_name
        self.batch_size=batch_size
        self.batch_window=batch_window


    def render(self) -> queue_event_model:
        return queue_event_model(
            original_resource_name=self.queue_name,
            original_resource_type=self.RUUID,
            event_type=EventTypes.QUEUE_TRIGGER,
            batch_size=self.batch_size,
            batch_window=self.batch_window,
        )


class QueuePermissions:
    RUUID = "cdev::simple::queue"

    def __init__(self, resource_name) -> None:
        self.READ_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
            ],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.WRITE_QUEUE = Permission(
            actions=[
                "sqs:SendMessage",
                "sqs:GetQueueAttributes",
            ],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_AND_WRITE_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:SendMessage",
            ],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_EVENTS = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
            ],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )


class simple_queue_model(ResourceModel):
    queue_name: str
    fifo: bool


class simple_queue_output(str, Enum):
    cloud_id = "cloud_id"
    queue_name = "queue_name"


class Queue(Resource):
    RUUID = "cdev::simple::queue"

    def __init__(self, cdev_name: str, queue_name: str, is_fifo: bool = False) -> None:
        """
        A simple sqs queue.

        args:
            cdev_name (str): Name of the resource
            queue_name (str, optional): Name of the queue in aws. Defaults to cdev_name if not provided.
            is_fifo (bool, optional, default=False): if this should be a First-in First-out queue (link to difference)
        """
        super().__init__(cdev_name)

        self.queue_name = queue_name if queue_name else "cdevqueue"

        self.fifo = is_fifo
        self.permissions = QueuePermissions(cdev_name)

        self.hash = hasher.hash_list([self.queue_name, is_fifo])

    def render(self) -> simple_queue_model:
        return simple_queue_model(
            **{
                "ruuid": self.RUUID,
                "name": self.name,
                "hash": self.hash,
                "queue_name": self.queue_name,
                "fifo": self.fifo,
            }
        )

    def create_event_trigger(
        self, batch_size: int = 10, batch_window: int = 5
    ) -> QueueEvent:
    
        # https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-eventsource
        if self.fifo and batch_size > 10:
            raise Exception

        event = QueueEvent(
            queue_name=self.queue_name,
            batch_size=batch_size,
            batch_window=batch_window
        )

        return event

    def from_output(self, key: simple_queue_output) -> Cloud_Output:
        return super().from_output(key)
