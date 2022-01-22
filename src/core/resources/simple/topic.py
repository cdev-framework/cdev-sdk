from enum import Enum

from core.constructs.resource import Resource, ResourceModel, Cloud_Output, update_hash
from core.utils import hasher

from .iam import Permission

RUUID = "cdev::simple::topic"


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
            cloud_id=f"{RUUID}::{resource_name}",
            effect="Allow",
        )

        self.PUBLISH = Permission(
            actions=["sns:GetTopicAttributes", "sns:Publish"],
            cloud_id=f"{RUUID}::{resource_name}",
            effect="Allow",
        )


##############
##### Output
##############
class simple_topic_output(str, Enum):
    cloud_id = "cloud_id"
    topic_name = "topic_name"


###############
##### Topic
###############
class simple_topic_model(ResourceModel):
    is_fifo: bool


class Topic(Resource):
    """Simple SNS topic.
    
    """

    @update_hash
    def __init__(
        self, cdev_name: str, is_fifo: bool = False, nonce: str = ''
    ) -> None:
        
        super().__init__(cdev_name, RUUID, nonce)

        self._is_fifo = is_fifo
        self.permissions = TopicPermissions(cdev_name)
    
    @property
    def is_fifo(self):
        return self._is_fifo

    @is_fifo.setter
    @update_hash
    def is_fifo(self, value: bool):
        self._is_fifo = value

    def compute_hash(self):
        self._hash = hasher.hash_list([self.is_fifo, self.nonce])

    def render(self) -> simple_topic_model:
        return simple_topic_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            is_fifo=self.is_fifo,
        )

    def from_output(self, key: simple_topic_output) -> Cloud_Output:
        return super().from_output(key)

