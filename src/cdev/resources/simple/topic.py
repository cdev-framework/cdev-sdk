from enum import Enum
from typing import List, Dict, Union

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher

from .xlambda import Event as lambda_event, EventTypes
from .iam import Permission

RUUID = "cdev::simple::topic"


class TopicPermissions:
    RUUID = "cdev::simple::topic"

    def __init__(self, resource_name) -> None:
        self.SUBSCRIBE = Permission(
            actions=[
                "sns:GetTopicAttributes",
                "sns:Subscribe",
            ],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.PUBLISH = Permission(
            actions=["sns:GetTopicAttributes", "sns:Publish"],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )


class simple_topic_model(ResourceModel):
    topic_name: str
    fifo: bool


class simple_topic_output(str, Enum):
    cloud_id = "cloud_id"
    topic_name = "topic_name"


class Topic(Resource):

    RUUID = "cdev::simple::topic"

    def __init__(
        self, cdev_name: str, topic_name: str = "", is_fifo: bool = False
    ) -> None:
        """
        Simple SNS topic.
        """
        super().__init__(cdev_name)

        self.topic_name = topic_name if topic_name else "cdevtopic"

        self.fifo = is_fifo
        self.permissions = TopicPermissions(cdev_name)

        self.hash = hasher.hash_list([self.topic_name, is_fifo])

    def render(self) -> simple_topic_model:
        return simple_topic_model(
            **{
                "ruuid": self.RUUID,
                "name": self.name,
                "hash": self.hash,
                "topic_name": self.topic_name,
                "fifo": self.fifo,
            }
        )

    def create_lambda_event_trigger(self) -> lambda_event:
        config = {}

        event = lambda_event(
            **{
                "original_resource_name": self.name,
                "original_resource_type": self.RUUID,
                "event_type": EventTypes.TOPIC_TRIGGER,
                "config": config,
            }
        )

        return event

    def from_output(self, key: simple_topic_output) -> Cloud_Output:
        return super().from_output(key)

