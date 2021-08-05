from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Callable, Any


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .s3_models import *


class Bucket(Cdev_Resource):
    """
    Deletes the S3 bucket. All objects (including all object versions and delete markers) in the bucket must be deleted before the bucket itself can be deleted.

  **Related Resources** 

 *  [CreateBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html) 


*  [DeleteObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html) 



    """

    def __init__(self,name: str, Bucket: str, ACL: BucketCannedACL=None, CreateBucketConfiguration: CreateBucketConfiguration=None, GrantFullControl: str=None, GrantRead: str=None, GrantReadACP: str=None, GrantWrite: str=None, GrantWriteACP: str=None, ObjectLockEnabledForBucket: bool=None):
        ""
        super().__init__(name)

        self.ACL = ACL
        """
        The canned ACL to apply to the bucket.


        """

        self.Bucket = Bucket
        """
        The name of the bucket to create.


        """

        self.CreateBucketConfiguration = CreateBucketConfiguration
        """
        The configuration information for the bucket.


        """

        self.GrantFullControl = GrantFullControl
        """
        Allows grantee the read, write, read ACP, and write ACP permissions on the bucket.


        """

        self.GrantRead = GrantRead
        """
        Allows grantee to list the objects in the bucket.


        """

        self.GrantReadACP = GrantReadACP
        """
        Allows grantee to read the bucket ACL.


        """

        self.GrantWrite = GrantWrite
        """
        Allows grantee to create new objects in the bucket.

 For the bucket and object owners of existing objects, also allows deletions and overwrites of those objects.


        """

        self.GrantWriteACP = GrantWriteACP
        """
        Allows grantee to write the ACL for the applicable bucket.


        """

        self.ObjectLockEnabledForBucket = ObjectLockEnabledForBucket
        """
        Specifies whether you want S3 Object Lock to be enabled for the new bucket.


        """

        self.hash = hasher.hash_list([self.Bucket, self.ACL, self.CreateBucketConfiguration, self.GrantFullControl, self.GrantRead, self.GrantReadACP, self.GrantWrite, self.GrantWriteACP, self.ObjectLockEnabledForBucket])

    def render(self) -> bucket_model:
        data = {
            "ruuid": "cdev::aws::s3::bucket",
            "name": self.name,
            "hash": self.hash,
            "ACL": self.ACL,
            "Bucket": self.Bucket,
            "CreateBucketConfiguration": self.CreateBucketConfiguration,
            "GrantFullControl": self.GrantFullControl,
            "GrantRead": self.GrantRead,
            "GrantReadACP": self.GrantReadACP,
            "GrantWrite": self.GrantWrite,
            "GrantWriteACP": self.GrantWriteACP,
            "ObjectLockEnabledForBucket": self.ObjectLockEnabledForBucket,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return bucket_model(**filtered_data)

    def from_output(self, key: bucket_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::s3::bucket::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::s3::bucket::{self.hash}", "key": key, "type": "cdev_output"})


