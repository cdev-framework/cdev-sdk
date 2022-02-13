from enum import Enum
from typing import Any

from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs, PermissionsAvailableMixin
from core.constructs.cloud_output import Cloud_Output_Str, OutputType
from core.constructs.types import cdev_str_model

from core.default.resources.simple.events import Event, event_model
from core.default.resources.simple.iam import Permission

from core.utils import hasher

RUUID = "cdev::simple::topic"


######################
##### Events
######################
class topic_event_model(event_model):
    """
    something

    Arguments:
        batch_size: int
        batch_window: int
    """
    topic_arn: cdev_str_model   


class TopicEvent(Event):
    
    def __init__(self, topic_name: str) -> None:

        self.cdev_topic_name = topic_name

        self.topic_arn = Cloud_Output_Str(
                name=topic_name, 
                ruuid=RUUID, 
                key='arn',
                type=OutputType.RESOURCE 
            )


    def render(self) -> topic_event_model:
        return topic_event_model(
            originating_resource_name=self.cdev_topic_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            topic_arn=self.topic_arn.render(),
        )


    def hash(self) -> str:
        return hasher.hash_list([
            self.cdev_topic_name,
        ])


#####################
###### Permission
######################
class TopicPermissions:
    def __init__(self, resource_name) -> None:
        self.SUBSCRIBE = Permission(
            actions=[
                "sns:GetTopicAttributes",
                "sns:Subscribe",
            ],
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
            effect="Allow",
        )

        self.PUBLISH = Permission(
            actions=[
                "sns:GetTopicAttributes",
                "sns:Publish"
            ],
            cloud_id=Cloud_Output_Str(resource_name, RUUID, 'cloud_id', OutputType.RESOURCE),
            effect="Allow",
        )


##############
##### Output
##############
class TopicOutput(ResourceOutputs):
    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def topic_name(self) -> Cloud_Output_Str:
        """The name of the generated table"""
        return Cloud_Output_Str(
            name=self._name,
            ruuid=RUUID,
            key='topic_name',
            type=self.OUTPUT_TYPE
        )

    @topic_name.setter
    def topic_name(self, value: Any):
        raise Exception


###############
##### Topic
###############
class simple_topic_model(ResourceModel):
    is_fifo: bool


class Topic(PermissionsAvailableMixin, Resource):
    """Simple SNS topic.
    
    """

    @update_hash
    def __init__(
        self, cdev_name: str, is_fifo: bool = False, nonce: str = ''
    ) -> None:
        """[summary]

        Args:
            cdev_name (str): [description]
            is_fifo (bool, optional): [description]. Defaults to False.
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
        """
        super().__init__(cdev_name, RUUID, nonce)

        self._is_fifo = is_fifo
        self.output = TopicOutput(cdev_name)
        self.available_permissions: TopicPermissions = TopicPermissions(cdev_name)
        self._event = None

    @property
    def is_fifo(self):
        return self._is_fifo

    @is_fifo.setter
    @update_hash
    def is_fifo(self, value: bool):
        self._is_fifo = value

    def create_event_trigger(
        self
    ) -> TopicEvent:
        if self._event:
            raise Exception("Already created an event on this topic. Use `get_event()` to get the current event.")
    

        event = TopicEvent(
            topic_name=self.name,
        )

        self._event = event

        return event

    def get_event(self) -> TopicEvent:
        if not self._event:
            raise Exception("Topic Event has not been created. Create a Topic Event for this topic using the `create_event_trigger` function before calling this function.")

        return self._event

    def compute_hash(self):
        self._hash = hasher.hash_list([self.is_fifo, self.nonce])

    def render(self) -> simple_topic_model:
        return simple_topic_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            is_fifo=self.is_fifo,
        )

