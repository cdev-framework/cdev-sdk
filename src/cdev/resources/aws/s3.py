from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .s3_models import *


class Bucket(Cdev_Resource):
    """
    Creates a new S3 bucket. To create a bucket, you must register with Amazon S3 and have a valid AWS Access Key ID to authenticate requests. Anonymous requests are never allowed to create buckets. By creating the bucket, you become the bucket owner.

 Not every string is an acceptable bucket name. For information about bucket naming restrictions, see [Bucket naming rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html).

 If you want to create an Amazon S3 on Outposts bucket, see [Create Bucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_control_CreateBucket.html). 

 By default, the bucket is created in the US East (N. Virginia) Region. You can optionally specify a Region in the request body. You might choose a Region to optimize latency, minimize costs, or address regulatory requirements. For example, if you reside in Europe, you will probably find it advantageous to create buckets in the Europe (Ireland) Region. For more information, see [Accessing a bucket](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html#access-bucket-intro).

  If you send your create bucket request to the `s3.amazonaws.com` endpoint, the request goes to the us-east-1 Region. Accordingly, the signature calculations in Signature Version 4 must use us-east-1 as the Region, even if the location constraint in the request specifies another Region where the bucket is to be created. If you create a bucket in a Region other than US East (N. Virginia), your application must be able to handle 307 redirect. For more information, see [Virtual hosting of buckets](https://docs.aws.amazon.com/AmazonS3/latest/dev/VirtualHosting.html).

  When creating a bucket using this operation, you can optionally specify the accounts or groups that should be granted specific permissions on the bucket. There are two ways to grant the appropriate permissions using the request headers.

 * Specify a canned ACL using the `x-amz-acl` request header. Amazon S3 supports a set of predefined ACLs, known as *canned ACLs*. Each canned ACL has a predefined set of grantees and permissions. For more information, see [Canned ACL](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#CannedACL).


* Specify access permissions explicitly using the `x-amz-grant-read`, `x-amz-grant-write`, `x-amz-grant-read-acp`, `x-amz-grant-write-acp`, and `x-amz-grant-full-control` headers. These headers map to the set of permissions Amazon S3 supports in an ACL. For more information, see [Access control list (ACL) overview](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html).

 You specify each grantee as a type=value pair, where the type is one of the following:


	+  `id` – if the value specified is the canonical user ID of an AWS account
	
	
	+  `uri` – if you are granting permissions to a predefined group
	
	
	+  `emailAddress` – if the value specified is the email address of an AWS account
	
	  Using email addresses to specify a grantee is only supported in the following AWS Regions: 
	
	 
		- US East (N. Virginia)
		
		
		- US West (N. California)
		
		
		-  US West (Oregon)
		
		
		-  Asia Pacific (Singapore)
		
		
		- Asia Pacific (Sydney)
		
		
		- Asia Pacific (Tokyo)
		
		
		- Europe (Ireland)
		
		
		- South America (São Paulo) For a list of all the Amazon S3 supported Regions and endpoints, see [Regions and Endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region) in the AWS General Reference.For example, the following `x-amz-grant-read` header grants the AWS accounts identified by account IDs permissions to read object data and its metadata:

  `x-amz-grant-read: id="11112222333", id="444455556666"`  



  You can use either a canned ACL or specify access permissions explicitly. You cannot do both.

  The following operations are related to `CreateBucket`:

 *  [PutObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html) 


*  [DeleteBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteBucket.html) 



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