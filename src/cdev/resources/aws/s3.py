from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .s3_models import *


class Bucket(Cdev_Resource):
    """
    Returns some or all (up to 1,000) of the objects in a bucket. You can use the request parameters as selection criteria to return a subset of the objects in a bucket. A 200 OK response can contain valid or invalid XML. Be sure to design your application to parse the contents of the response and handle it appropriately.

  This action has been revised. We recommend that you use the newer version, [ListObjectsV2](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html), when developing applications. For backward compatibility, Amazon S3 continues to support `ListObjects`.

  The following operations are related to `ListObjects`:

 *  [ListObjectsV2](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html) 


*  [GetObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html) 


*  [PutObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html) 


*  [CreateBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html) 


*  [ListBuckets](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListBuckets.html) 



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

    def from_output(self, key: bucket_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::aws::s3::bucket::{self.hash}", "key": key})


class s3_object(BaseModel):
    S3Bucket: str
    S3Key: str