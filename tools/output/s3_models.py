from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict, Union

from ...models import Cloud_Output, Rendered_Resource

from ...backend import cloud_mapper_manager

class BucketCannedACL(str, Enum): 


    private = 'private'
    
    public_read = 'public-read'
    
    public_read_write = 'public-read-write'
    
    authenticated_read = 'authenticated-read'
    


class BucketLocationConstraint(str, Enum): 


    af_south_1 = 'af-south-1'
    
    ap_east_1 = 'ap-east-1'
    
    ap_northeast_1 = 'ap-northeast-1'
    
    ap_northeast_2 = 'ap-northeast-2'
    
    ap_northeast_3 = 'ap-northeast-3'
    
    ap_south_1 = 'ap-south-1'
    
    ap_southeast_1 = 'ap-southeast-1'
    
    ap_southeast_2 = 'ap-southeast-2'
    
    ca_central_1 = 'ca-central-1'
    
    cn_north_1 = 'cn-north-1'
    
    cn_northwest_1 = 'cn-northwest-1'
    
    EU = 'EU'
    
    eu_central_1 = 'eu-central-1'
    
    eu_north_1 = 'eu-north-1'
    
    eu_south_1 = 'eu-south-1'
    
    eu_west_1 = 'eu-west-1'
    
    eu_west_2 = 'eu-west-2'
    
    eu_west_3 = 'eu-west-3'
    
    me_south_1 = 'me-south-1'
    
    sa_east_1 = 'sa-east-1'
    
    us_east_2 = 'us-east-2'
    
    us_gov_east_1 = 'us-gov-east-1'
    
    us_gov_west_1 = 'us-gov-west-1'
    
    us_west_1 = 'us-west-1'
    
    us_west_2 = 'us-west-2'
    

class CreateBucketConfiguration(BaseModel):
    """
    The configuration information for the bucket.


    """


    LocationConstraint: Union[BucketLocationConstraint, Cloud_Output]
    """
    Specifies the Region where the bucket will be created. If you don't specify a Region, the bucket is created in the US East (N. Virginia) Region (us-east-1).


    """


    def __init__(self, LocationConstraint: BucketLocationConstraint ):
        "My doc string"
        super().__init__(**{
            "LocationConstraint": LocationConstraint,
        })        










class bucket_output(str, Enum):
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

    Location = "Location"



class bucket_model(Rendered_Resource):
    """

    Deletes the S3 bucket. All objects (including all object versions and delete markers) in the bucket must be deleted before the bucket itself can be deleted.

  **Related Resources** 

 *  [CreateBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html) 


*  [DeleteObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html)
    
    """


    ACL: Optional[Union[BucketCannedACL, Cloud_Output]] 
    """
    The canned ACL to apply to the bucket.
    """

    Bucket: Union[str, Cloud_Output]
    """
    The name of the bucket to create.
    """

    CreateBucketConfiguration: Optional[Union[CreateBucketConfiguration, Cloud_Output]] 
    """
    The configuration information for the bucket.
    """

    GrantFullControl: Optional[Union[str, Cloud_Output]]
    """
    Allows grantee the read, write, read ACP, and write ACP permissions on the bucket.
    """

    GrantRead: Optional[Union[str, Cloud_Output]]
    """
    Allows grantee to list the objects in the bucket.
    """

    GrantReadACP: Optional[Union[str, Cloud_Output]]
    """
    Allows grantee to read the bucket ACL.
    """

    GrantWrite: Optional[Union[str, Cloud_Output]]
    """
    Allows grantee to create new objects in the bucket.

 For the bucket and object owners of existing objects, also allows deletions and overwrites of those objects.
    """

    GrantWriteACP: Optional[Union[str, Cloud_Output]]
    """
    Allows grantee to write the ACL for the applicable bucket.
    """

    ObjectLockEnabledForBucket: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether you want S3 Object Lock to be enabled for the new bucket.
    """


    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['Bucket', 'ACL', 'CreateBucketConfiguration', 'GrantFullControl', 'GrantRead', 'GrantReadACP', 'GrantWrite', 'GrantWriteACP', 'ObjectLockEnabledForBucket'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['Bucket', 'ExpectedBucketOwner'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


