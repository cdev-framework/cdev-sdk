from enum import Enum

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher

from .xlambda import Event as lambda_event
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
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.PUBLISH = Permission(
            actions=["sns:GetTopicAttributes", "sns:Publish"],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )


class simple_topic_model(ResourceModel):
    
    fifo: bool


class simple_topic_output(str, Enum):
    cloud_id = "cloud_id"
    topic_name = "topic_name"


class Topic(Resource):

    RUUID = "cdev::simple::topic"

    def __init__(
        self, cdev_name: str, is_fifo: bool = False, _nonce: str=''
    ) -> None:
        """
        Simple SNS topic.
        """
        super().__init__(cdev_name)

        self.fifo = is_fifo
        self.permissions = TopicPermissions(cdev_name)
        self._nonce = _nonce

        self.hash = hasher.hash_list([is_fifo, self._nonce])

    def render(self) -> simple_topic_model:
        return simple_topic_model(
            **{
                "ruuid": self.RUUID,
                "name": self.name,
                "hash": self.hash,
                "fifo": self.fifo,
            }
        )

    def create_lambda_event_trigger(self) -> lambda_event:
        config = {}

        event = lambda_event(
            **{
                "original_resource_name": self.name,
                "original_resource_type": self.RUUID,
                "event_type": "",
                "config": config,
            }
        )

        return event

    def from_output(self, key: simple_topic_output) -> Cloud_Output:
        return super().from_output(key)

