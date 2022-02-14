"""Set of constructs for making message queues

"""
from os import name
from typing import Any

from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs, PermissionsAvailableMixin
from core.constructs.cloud_output import  Cloud_Output_Str, OutputType
from core.constructs.types import cdev_str_model

from core.default.resources.simple.events import Event, event_model
from core.default.resources.simple.iam import Permission

from core.utils import hasher

RUUID = "cdev::simple::queue"


######################
##### Events
######################
class queue_event_model(event_model):
    """
    something

    Arguments:
        batch_size: int
        batch_window: int
    """
    queue_arn: cdev_str_model   
    batch_size: int


class QueueEvent(Event):
    
    def __init__(self, queue_name: str, batch_size: int) -> None:

        if batch_size > 10000 or batch_size < 0:
            raise Exception

        self.cdev_queue_name = queue_name

        self.queue_arn = Cloud_Output_Str(
                name=queue_name, 
                ruuid=RUUID, 
                key='arn',
                type=OutputType.RESOURCE 
            )

        self.batch_size = batch_size


    def render(self) -> queue_event_model:
        return queue_event_model(
            originating_resource_name=self.cdev_queue_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            queue_arn=self.queue_arn.render(),
            batch_size=self.batch_size
        )


    def hash(self) -> str:
        return hasher.hash_list([
            self.cdev_queue_name,
            self.batch_size
        ])

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
        self._event = None
        self.available_permissions: QueuePermissions = QueuePermissions(cdev_name)

    @property
    def is_fifo(self):
        return self._is_fifo

    @is_fifo.setter
    @update_hash
    def is_fifo(self, value: bool):
        self._is_fifo = value

    def create_event_trigger(
        self, batch_size: int = 10
    ) -> QueueEvent:
        if self._event:
            raise Exception("Already created stream on this table. Use `get_stream()` to get the current stream.")
    
        # https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-eventsource
        if self.is_fifo and batch_size > 10:
            raise Exception

        event = QueueEvent(
            queue_name=self.name,
            batch_size=batch_size,
        )

        self._event = event

        return event

    def get_event(self) -> QueueEvent:
        if not self._event:
            raise Exception("Queue Event has not been created. Create a stream for this table using the `create_stream` function before calling this function.")

        return self._event

        
    def compute_hash(self):
        self._hash = hasher.hash_list([self.is_fifo, self.nonce])
        
    def render(self) -> simple_queue_model:
        return simple_queue_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            is_fifo=self.is_fifo,
        )
