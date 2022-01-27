from enum import Enum
from typing import Any

from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs
from core.constructs.output import Cloud_Output_Str, OutputType
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


class Topic(Resource):
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

