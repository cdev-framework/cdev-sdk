from enum import Enum
from typing import List, Dict, Union


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher, environment as cdev_environment

from .xlambda import Event as lambda_event, EventTypes, Permission

RUUID = 'cdev::simple::bucket'

class Bucket_Event_Types(Enum):
    Object_Created = "s3:ObjectCreated:*"
    Object_Removed = "s3:ObjectRemoved:*"
    Object_Restore = "s3:ObjectRestore:*"
    Object_Replicaton = "s3:ObjectReplication:*"


class BucketPermissions():
    def __init__(self, resource_name) -> None:
        self.READ_BUCKET = Permission(
            actions=[
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:ListBucket"
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )
    
        self.WRITE_BUCKET = Permission(
            actions=[
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:ListBucket"
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )
    
        self.READ_AND_WRITE_BUCKET = Permission(
            actions=[   
                "s3:*Object",
                "s3:ListBucket"
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )
    
        self.READ_EVENTS = Permission(
            actions=[
                "s3:*Object",
                "s3:ListBucket"
            ],
            resource=f'{RUUID}::{resource_name}',
            effect="Allow"
        )


class simple_bucket_model(Rendered_Resource):
    bucket_name: str
    


class simple_bucket_output(str, Enum):
    cloud_id = "cloud_id"
    bucket_name = "bucket_name"



class Bucket(Cdev_Resource):
    def __init__(self, cdev_name: str, bucket_name: str) -> None:
        
        super().__init__(cdev_name)

        self.bucket_name = f"{bucket_name}_{cdev_environment.get_current_environment_hash()}"

        self.permissions = BucketPermissions(cdev_name)

        self.hash = hasher.hash_list([self.bucket_name])

    def render(self) -> simple_bucket_model:
        return simple_bucket_model(**{
            "ruuid": RUUID,
            "name": self.name,
            "hash": self.hash ,
            "bucket_name": self.bucket_name,
            }
        )

    def create_event_trigger(self, event_types: List[Bucket_Event_Types]) -> lambda_event:
        config = {
            "EventTypes": list(set([x.value for x in event_types])),
        }

        event = lambda_event(**{
            "original_resource_name": self.name,
            "original_resource_type": RUUID,
            "event_type": EventTypes.BUCKET_TRIGGER,
            "config": config
            }
        )

        return event


    def from_output(self, key: simple_bucket_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::simple::bucket::{self.hash}", "key": key.value, "type": "cdev_output"})