from enum import Enum
from typing import List, Dict, Union


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .xlambda import Event as lambda_event, EventTypes, Permission

RUUID = 'cdev::simple::topic'

class TopicPermissions():
    def __init__(self, resource_name) -> None:
        self.SUBSCRIBE = Permission(
            actions=[
                "sns:GetTopicAttributes",
                "sns:Subscribe",
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )
    
        self.PUBLISH = Permission(
            actions=[
                "sns:GetTopicAttributes",
                "sns:Publish"
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )


class simple_topic_model(Rendered_Resource):
    topic_name: str
    fifo: bool
    

class simple_topic_output(str, Enum):
    cloud_id = "cloud_id"
    topic_name = "topic_name"


class Topic(Cdev_Resource):
    def __init__(self, cdev_name: str, topic_name: str, is_fifo: bool = False) -> None:
        
        super().__init__(cdev_name)
        self.topic_name = topic_name if not is_fifo else f"{topic_name}.fifo"
        self.fifo = is_fifo
        self.permissions = TopicPermissions(cdev_name)

        self.hash = hasher.hash_list([self.topic_name, is_fifo])

    def render(self) -> simple_topic_model:
        return simple_topic_model(**{
            "ruuid": RUUID,
            "name": self.name,
            "hash": self.hash ,
            "topic_name": self.topic_name,
            "fifo": self.fifo
            }
        )

    def create_lambda_event_trigger(self) -> lambda_event:
        config = {
            
        }

        event = lambda_event(**{
            "original_resource_name": self.name,
            "original_resource_type": RUUID,
            "event_type": EventTypes.TOPIC_TRIGGER,
            "config": config
            }
        )

        return event


    def from_output(self, key: simple_topic_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"{RUUID}::{self.hash}", "key": key.value, "type": "cdev_output"})