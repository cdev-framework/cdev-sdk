"""Set of constructs for creating Cloud Object Stores like S3

"""

from enum import Enum
from typing import Any, Dict

from core.constructs.resource import (
    Resource,
    TaggableResourceModel,
    update_hash,
    ResourceOutputs,
    PermissionsAvailableMixin,
    TaggableMixin,
)
from core.constructs.cloud_output import Cloud_Output_Str, OutputType
from core.constructs.types import cdev_str_model
from core.utils import hasher
from core.constructs.models import frozendict

from core.default.resources.simple.iam import Permission

from core.default.resources.simple.events import Event, event_model

RUUID = "cdev::simple::bucket"


class Bucket_Event_Type(str, Enum):
    Object_Created = "s3:ObjectCreated:*"
    """Receive Events when Objects are created in the `Bucket`"""
    Object_Removed = "s3:ObjectRemoved:*"
    """Receive Events when Objects are removed from the `Bucket`"""
    Object_Restore = "s3:ObjectRestore:*"
    """Receive Events when Objects are restored to the `Bucket`"""
    Object_Replicaton = "s3:ObjectReplication:*"
    """Receive Events when Objects are replicated to the `Bucket`"""


class bucket_event_model(event_model):
    """Model representing an Event from a Bucket

    Args:
        bucket_arn (cdev_str_model)
        bucket_name (cdev_str_model)
        bucket_event_type (Bucket_Event_Type)
    """

    bucket_arn: cdev_str_model
    bucket_name: cdev_str_model
    bucket_event_type: Bucket_Event_Type


class BucketEvent(Event):
    """Construct representing an Event from a Bucket"""

    def __init__(self, bucket_name: str, bucket_event_type: Bucket_Event_Type) -> None:
        """
        Args:
            bucket_name (str): Cdev name of the bucket
            bucket_event_type (Bucket_Event_Type): Type fo events to create
        """
        self.bucket_cdev_name = bucket_name
        self.bucket_event_type = bucket_event_type
        self.bucket_arn = Cloud_Output_Str(
            name=bucket_name, ruuid=RUUID, key="cloud_id", type=OutputType.RESOURCE
        )
        self.bucket_name = Cloud_Output_Str(
            name=bucket_name, ruuid=RUUID, key="bucket_name", type=OutputType.RESOURCE
        )

    def render(self) -> bucket_event_model:
        return bucket_event_model(
            originating_resource_name=self.bucket_cdev_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            bucket_event_type=self.bucket_event_type,
            bucket_arn=self.bucket_arn.render(),
            bucket_name=self.bucket_name.render(),
        )

    def hash(self) -> str:
        return hasher.hash_list([self.bucket_cdev_name, self.bucket_event_type])


class BucketPermissions:
    RUUID = "cdev::simple::bucket"

    def __init__(self, resource_name: str) -> None:

        self.LIST_BUCKET = Permission(
            actions=["s3:ListBucket"],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ),
            effect="Allow",
        )
        """Permissions to list objects from the `Bucket`"""

        self.READ_BUCKET = Permission(
            actions=["s3:GetObject", "s3:GetObjectVersion"],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ).join(["", "/*"]),
            effect="Allow",
        )
        """Permissions to read objects from the `Bucket`"""

        self.WRITE_BUCKET = Permission(
            actions=["s3:PutObject", "s3:PutObjectAcl"],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ).join(["", "/*"]),
            effect="Allow",
        )
        """Permissions to write objects to the `Bucket`"""

        self.READ_AND_WRITE_BUCKET = Permission(
            actions=["s3:*Object"],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ).join(["", "/*"]),
            effect="Allow",
        )
        """Permissions to read and write objects to and from the `Bucket`"""

        self.READ_EVENTS = Permission(
            actions=["s3:*Object"],
            cloud_id=Cloud_Output_Str(
                resource_name, RUUID, "cloud_id", OutputType.RESOURCE
            ).join(["", "/*"]),
            effect="Allow",
        )
        """Permissions to receive events from the `Bucket`"""


class bucket_model(TaggableResourceModel):
    """Model representing a Bucket"""

    pass


class BucketOutput(ResourceOutputs):
    """Container object for the returned values from the cloud after a Bucket has been deployed."""

    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def bucket_name(self) -> Cloud_Output_Str:
        """The name of the generated bucket"""
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="bucket_name", type=self.OUTPUT_TYPE
        )

    @bucket_name.setter
    def bucket_name(self, value: Any) -> None:
        raise Exception


class Bucket(PermissionsAvailableMixin, TaggableMixin, Resource):
    """A Simple Bucket is a basic object store for applications to build on."""

    @update_hash
    def __init__(
        self,
        cdev_name: str,
        nonce: str = "",
        tags: Dict[str, str] = None,
    ) -> None:
        """
        Args:
            cdev_name (str): Name of the resource
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
            tags (Dict[str, str]): A set of tags to add to the resource
        """
        super().__init__(cdev_name, RUUID, nonce, tags=tags)

        self.available_permissions: BucketPermissions = BucketPermissions(cdev_name)
        self.output = BucketOutput(cdev_name)

    def create_event_trigger(self, event_type: Bucket_Event_Type) -> BucketEvent:
        """Create Construct of event that other resources can respond to"""

        event = BucketEvent(bucket_name=self.name, bucket_event_type=event_type)

        return event

    def compute_hash(self) -> None:
        self._hash = hasher.hash_list(
            [
                self.nonce,
                self._get_tags_hash(),
            ]
        )

    def render(self) -> bucket_model:
        return bucket_model(
            ruuid=self.ruuid,
            name=self.name,
            hash=self.hash,
            tags=frozendict(self.tags)
        )
