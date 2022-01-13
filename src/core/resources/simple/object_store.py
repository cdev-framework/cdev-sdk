from enum import Enum
from typing import List, Dict, Union

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher

from .xlambda import Event as lambda_event, EventTypes
from .iam import Permission

class Bucket_Event_Types(str, Enum):
    Object_Created = "s3:ObjectCreated:*"
    Object_Removed = "s3:ObjectRemoved:*"
    Object_Restore = "s3:ObjectRestore:*"
    Object_Replicaton = "s3:ObjectReplication:*"


class BucketPermissions:

    RUUID = "cdev::simple::bucket"

    def __init__(self, resource_name) -> None:
        self.READ_BUCKET = Permission(
            actions=["s3:GetObject", "s3:GetObjectVersion", "s3:ListBucket"],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.WRITE_BUCKET = Permission(
            actions=["s3:PutObject", "s3:PutObjectAcl", "s3:ListBucket"],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_AND_WRITE_BUCKET = Permission(
            actions=["s3:*Object", "s3:ListBucket"],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_EVENTS = Permission(
            actions=["s3:*Object", "s3:ListBucket"],
            resource=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )


class simple_bucket_model(ResourceModel):
    bucket_name: str


class simple_bucket_output(str, Enum):
    cloud_id = "cloud_id"
    cloud_name = "cloud_name"


class Bucket(Resource):
    RUUID = "cdev::simple::bucket"

    def __init__(self, cdev_name: str, bucket_name: str = "") -> None:
        """
        Create a simple S3 bucket that can be used as an object store.

        Args:
            cdev_name (str): Name of the resource
            bucket_name (str, optional): base name of the bucket in s3. If not provided, will default to cdev_name.
        """
        super().__init__(cdev_name)

        self.bucket_name = (
            bucket_name
            if bucket_name
            else "bucket"
        )

        self.permissions = BucketPermissions(cdev_name)

        self.hash = hasher.hash_list([self.bucket_name])

    def render(self) -> simple_bucket_model:
        return simple_bucket_model(
            **{
                "ruuid": self.RUUID,
                "name": self.name,
                "hash": self.hash,
                "bucket_name": self.bucket_name,
            }
        )

    def create_event_trigger(
        self, event_types: List[Bucket_Event_Types]
    ) -> lambda_event:
        config = {
            "EventTypes": list(set([x.value for x in event_types])),
        }

        event = lambda_event(
            **{
                "original_resource_name": self.name,
                "original_resource_type": self.RUUID,
                "event_type": EventTypes.BUCKET_TRIGGER,
                "config": config,
            }
        )

        return event

    def from_output(self, key: simple_bucket_output) -> Cloud_Output:
        return super().from_output(key)
