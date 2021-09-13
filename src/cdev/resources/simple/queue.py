from enum import Enum
from typing import List, Dict, Union


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .xlambda import Event as lambda_event, EventTypes, Permission

RUUID = 'cdev::simple::queue'



class QueuePermissions():
    def __init__(self, resource_name) -> None:
        self.READ_QUEUE = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )
    
        self.WRITE_QUEUE = Permission(
            actions=[
                "sqs:SendMessage",
                "sqs:GetQueueAttributes",
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )
    
        self.READ_AND_WRITE_QUEUE = Permission(
            actions=[   
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes",
                "sqs:SendMessage",
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )
    
        self.READ_EVENTS = Permission(
            actions=[
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )


class simple_queue_model(Rendered_Resource):
    queue_name: str
    fifo: bool
    


class simple_queue_output(str, Enum):
    cloud_id = "cloud_id"
    queue_name = "queue_name"



class Queue(Cdev_Resource):
    def __init__(self, cdev_name: str, queue_name: str, is_fifo: bool = False) -> None:
        
        super().__init__(cdev_name)
        self.queue_name = queue_name if not is_fifo else f"{queue_name}.fifo"
        self.fifo = is_fifo
        self.permissions = QueuePermissions(cdev_name)

        self.hash = hasher.hash_list([self.queue_name, is_fifo])

    def render(self) -> simple_queue_model:
        return simple_queue_model(**{
            "ruuid": RUUID,
            "name": self.name,
            "hash": self.hash ,
            "queue_name": self.queue_name,
            "fifo": self.fifo
            }
        )

    def create_event_trigger(self, batch_size: int = 10, batch_window: int = 5) -> lambda_event:
        if batch_size > 10000 or batch_size < 0:
            raise Exception

        # https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html#events-sqs-eventsource
        if self.fifo and batch_size > 10:
            raise Exception
        
        config = {
            "batch_size": batch_size,
            "batch_window": batch_window
        }

        event = lambda_event(**{
            "original_resource_name": self.name,
            "original_resource_type": RUUID,
            "event_type": EventTypes.QUEUE_TRIGGER,
            "config": config
            }
        )

        return event


    def from_output(self, key: simple_queue_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"{RUUID}::{self.hash}", "key": key.value, "type": "cdev_output"})