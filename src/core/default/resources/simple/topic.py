"""Set of constructs for making fan our message topics

"""
from typing import Any, Dict

from core.constructs.resource import (
    Resource,
    TaggableResourceModel,
    TaggableMixin,
    update_hash,
    ResourceOutputs,
    PermissionsAvailableMixin,
)
from core.constructs.cloud_output import Cloud_Output_Str, OutputType
from core.constructs.types import cdev_str_model
from core.constructs.models import frozendict

from core.default.resources.simple.events import Event, event_model
from core.default.resources.simple.iam import Permission

from core.utils import hasher

RUUID = "cdev::simple::topic"


######################
##### Events
######################
class topic_event_model(event_model):
    """Model representing a Topic event"""

    topic_arn: cdev_str_model


class TopicEvent(Event):
    """Construct representing the Events from the Topic"""

    def __init__(self, topic_name: str) -> None:

        self.cdev_topic_name = topic_name

        self.topic_arn = Cloud_Output_Str(
            name=topic_name, ruuid=RUUID, key="arn", type=OutputType.RESOURCE
        )

    def render(self) -> topic_event_model:
        return topic_event_model(
            originating_resource_name=self.cdev_topic_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            topic_arn=self.topic_arn.render(),
        )

    def hash(self) -> str:
        return hasher.hash_list(
            [
                self.cdev_topic_name,
            ]
        )


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
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to subscribe to the Topic"""

        self.PUBLISH = Permission(
            actions=["sns:GetTopicAttributes", "sns:Publish"],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permission to publish to the Topic"""


##############
##### Output
##############
class TopicOutput(ResourceOutputs):
    """Container object for the returned values from the cloud after a Topic has been deployed."""

    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def topic_name(self) -> Cloud_Output_Str:
        """The name of the generated topic"""
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="topic_name", type=self.OUTPUT_TYPE
        )

    @topic_name.setter
    def topic_name(self, value: Any) -> None:
        raise Exception


###############
##### Topic
###############
class simple_topic_model(TaggableResourceModel):
    """Model representing a Pub/Sub Topic"""

    is_fifo: bool
    """Should the Topic guarantee ordering of messages"""


class Topic(PermissionsAvailableMixin, TaggableMixin, Resource):
    """Construct for creating a managed SNS Pub/Sub Topic"""

    @update_hash
    def __init__(
        self,
        cdev_name: str,
        is_fifo: bool = False,
        nonce: str = "",
        tags: Dict[str, str] = None,
    ) -> None:
        """
        Args:
            cdev_name (str): Name of the resource.
            is_fifo (bool, default=False): If True, the Queue will guarantee ordering of messages.
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
            tags (Dict[str, str]): A set of tags to add to the resource
        """
        super().__init__(cdev_name, RUUID, nonce, tags=tags)

        self._is_fifo = is_fifo
        self.output = TopicOutput(cdev_name)
        self.available_permissions: TopicPermissions = TopicPermissions(cdev_name)
        self._event = None

    @property
    def is_fifo(self) -> bool:
        """Should the Pub/Sub Topic guarantee ordering of messages"""
        return self._is_fifo

    @is_fifo.setter
    @update_hash
    def is_fifo(self, value: bool) -> None:
        self._is_fifo = value

    def create_event_trigger(self) -> TopicEvent:
        """Create an Event for the Topic that other resources can listen to

        Raises:
            Exception: _description_
            Exception: _description_

        Returns:
            QueueEvent
        """
        if self._event:
            raise Exception(
                "Already created an event on this topic. Use `get_event()` to get the current event."
            )

        self._event = TopicEvent(
            topic_name=self.name,
        )

        return self._event

    def get_event(self) -> TopicEvent:
        """Get the Event for this Queue

        Raises:
            Exception: _description_

        Returns:
            QueueEvent
        """
        if not self._event:
            raise Exception(
                "Topic Event has not been created. "
                "Create a Topic Event for this topic using the `create_event_trigger` "
                "function before calling this function."
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

    def render(self) -> simple_topic_model:
        return simple_topic_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            is_fifo=self.is_fifo,
            tags=frozendict(self.tags)
        )
