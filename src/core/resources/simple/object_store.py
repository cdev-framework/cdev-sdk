from enum import Enum

from core.constructs.resource import Resource, ResourceModel, Cloud_Output, update_hash
from core.utils import hasher

from .iam import Permission

from .events import Event, event_model, EventTypes

RUUID = "cdev::simple::bucket"

class Bucket_Event_Type(str, Enum):
    Object_Created = "s3:ObjectCreated:*"
    Object_Removed = "s3:ObjectRemoved:*"
    Object_Restore = "s3:ObjectRestore:*"
    Object_Replicaton = "s3:ObjectReplication:*"


class bucket_event_model(event_model):
    """
    something

    Arguments:
        original_resource_name: str
        original_resource_type: str
        event_type: EventTypes
        bucket_event_type: Bucket_Event_Types
    """
    bucket_event_type: Bucket_Event_Type


class BucketEvent(Event):
    RUUID = "cdev::simple::bucket"

    def __init__(self, bucket_name: str, bucket_event_type: Bucket_Event_Type) -> None:
        self.bucket_name = bucket_name
        self.bucket_event_type = bucket_event_type


    def render(self) -> event_model:
        return bucket_event_model(
            original_resource_name=self.bucket_name,
            original_resource_type=self.RUUID,
            event_type=EventTypes.BUCKET_TRIGGER,
            bucket_event_type=self.bucket_event_type 
        )


class BucketPermissions:
    RUUID = "cdev::simple::bucket"

    def __init__(self, resource_name) -> None:
        self.READ_BUCKET = Permission(
            actions=["s3:GetObject", "s3:GetObjectVersion", "s3:ListBucket"],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.WRITE_BUCKET = Permission(
            actions=["s3:PutObject", "s3:PutObjectAcl", "s3:ListBucket"],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_AND_WRITE_BUCKET = Permission(
            actions=["s3:*Object", "s3:ListBucket"],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )

        self.READ_EVENTS = Permission(
            actions=["s3:*Object", "s3:ListBucket"],
            cloud_id=f"{self.RUUID}::{resource_name}",
            effect="Allow",
        )


class simple_bucket_model(ResourceModel):
    pass


class simple_bucket_output(str, Enum):
    cloud_id = "cloud_id"
    cloud_name = "cloud_name"


class SimpleBucket(Resource):
    
    @update_hash
    def __init__(self, cdev_name: str, nonce: str="") -> None:
        """
        Create a simple S3 bucket that can be used as an object store.

        Args:
            cdev_name (str): Name of the resource
        """
        super().__init__(cdev_name, RUUID, nonce)


        self.permissions = BucketPermissions(cdev_name)

        self.hash = hasher.hash_list([self._nonce])


    

    def create_event_trigger(
        self, event_type: Bucket_Event_Type
    ) -> BucketEvent:

        event = BucketEvent(
            bucket_name=self.name,
            bucket_event_type=event_type
        )

        return event

    def compute_hash(self):
        self._hash = hasher.hash_list([self.nonce])
        
    def render(self) -> simple_bucket_model:
        return simple_bucket_model(
            ruuid=self.ruuid,
            name=self.name,
            hash=self.hash,
        )

    def from_output(self, key: simple_bucket_output) -> Cloud_Output:
        return super().from_output(key)
