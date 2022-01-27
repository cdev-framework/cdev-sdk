from enum import Enum
from os import name
from typing import Any

from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs, PermissionsAvailableMixin
from core.constructs.output import  Cloud_Output_Str, OutputType
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

    def __init__(self, resource_name: str) -> None:
        self.READ_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
            effect="Allow",
        )

        self.WRITE_QUEUE = Permission(
            actions=[
                "sqs:SendMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
            effect="Allow",
        )

        self.READ_AND_WRITE_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:SendMessage",
            ],
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
            effect="Allow",
        )

        self.READ_EVENTS = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
            ],
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
            effect="Allow",
        )


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
            name=self._name,
            ruuid=RUUID,
            key='queue_name',
            type=self.OUTPUT_TYPE
        )

    @queue_name.setter
    def queue_name(self, value: Any):
        raise Exception


######################
##### Queue
######################
class simple_queue_model(ResourceModel):
    is_fifo: bool


class Queue(PermissionsAvailableMixin, Resource):

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
        self.output = QueueOutput(name)
        self.available_permissions = QueuePermissions(cdev_name)

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
