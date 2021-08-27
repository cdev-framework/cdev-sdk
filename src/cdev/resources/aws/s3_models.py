from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict, Union, Dict
from pathlib import Path

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









class ObjectCannedACL(str, Enum): 


    private = 'private'
    
    public_read = 'public-read'
    
    public_read_write = 'public-read-write'
    
    authenticated_read = 'authenticated-read'
    
    aws_exec_read = 'aws-exec-read'
    
    bucket_owner_read = 'bucket-owner-read'
    
    bucket_owner_full_control = 'bucket-owner-full-control'
    










class ServerSideEncryption(str, Enum): 


    AES256 = 'AES256'
    
    aws_kms = 'aws:kms'
    

class StorageClass(str, Enum): 


    STANDARD = 'STANDARD'
    
    REDUCED_REDUNDANCY = 'REDUCED_REDUNDANCY'
    
    STANDARD_IA = 'STANDARD_IA'
    
    ONEZONE_IA = 'ONEZONE_IA'
    
    INTELLIGENT_TIERING = 'INTELLIGENT_TIERING'
    
    GLACIER = 'GLACIER'
    
    DEEP_ARCHIVE = 'DEEP_ARCHIVE'
    
    OUTPOSTS = 'OUTPOSTS'
    







class RequestPayer(str, Enum): 
    """
    Confirms that the requester knows that they will be charged for the request. Bucket owners need not specify this parameter in their requests. For information about downloading objects from requester pays buckets, see [Downloading Objects in Requestor Pays Buckets](https://docs.aws.amazon.com/AmazonS3/latest/dev/ObjectsinRequesterPaysBuckets.html) in the *Amazon S3 User Guide*.


    """


    requester = 'requester'
    


class ObjectLockMode(str, Enum): 


    GOVERNANCE = 'GOVERNANCE'
    
    COMPLIANCE = 'COMPLIANCE'
    

class ObjectLockLegalHoldStatus(str, Enum): 


    ON = 'ON'
    
    OFF = 'OFF'
    




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



class object_output(str, Enum):
    """
    Adds an object to a bucket. You must have WRITE permissions on a bucket to add an object to it.

 Amazon S3 never adds partial objects; if you receive a success response, Amazon S3 added the entire object to the bucket.

 Amazon S3 is a distributed system. If it receives multiple write requests for the same object simultaneously, it overwrites all but the last object written. Amazon S3 does not provide object locking; if you need this, make sure to build it into your application layer or use versioning instead.

 To ensure that data is not corrupted traversing the network, use the `Content-MD5` header. When you use this header, Amazon S3 checks the object against the provided MD5 value and, if they do not match, returns an error. Additionally, you can calculate the MD5 while putting an object to Amazon S3 and compare the returned ETag to the calculated MD5 value.

   The `Content-MD5` header is required for any request to upload an object with a retention period configured using Amazon S3 Object Lock. For more information about Amazon S3 Object Lock, see [Amazon S3 Object Lock Overview](https://docs.aws.amazon.com/AmazonS3/latest/dev/object-lock-overview.html) in the *Amazon S3 User Guide*. 

   **Server-side Encryption** 

 You can optionally request server-side encryption. With server-side encryption, Amazon S3 encrypts your data as it writes it to disks in its data centers and decrypts the data when you access it. You have the option to provide your own encryption key or use AWS managed encryption keys (SSE-S3 or SSE-KMS). For more information, see [Using Server-Side Encryption](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html).

 If you request server-side encryption using AWS Key Management Service (SSE-KMS), you can enable an S3 Bucket Key at the object-level. For more information, see [Amazon S3 Bucket Keys](https://docs.aws.amazon.com/AmazonS3/latest/dev/bucket-key.html) in the *Amazon S3 User Guide*.

  **Access Control List (ACL)-Specific Request Headers** 

 You can use headers to grant ACL- based permissions. By default, all objects are private. Only the owner has full access control. When adding a new object, you can grant permissions to individual AWS accounts or to predefined groups defined by Amazon S3. These permissions are then added to the ACL on the object. For more information, see [Access Control List (ACL) Overview](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html) and [Managing ACLs Using the REST API](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-using-rest-api.html). 

  **Storage Class Options** 

 By default, Amazon S3 uses the STANDARD Storage Class to store newly created objects. The STANDARD storage class provides high durability and high availability. Depending on performance needs, you can specify a different Storage Class. Amazon S3 on Outposts only uses the OUTPOSTS Storage Class. For more information, see [Storage Classes](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html) in the *Amazon S3 User Guide*.

  **Versioning** 

 If you enable versioning for a bucket, Amazon S3 automatically generates a unique version ID for the object being stored. Amazon S3 returns this ID in the response. When you enable versioning for a bucket, if Amazon S3 receives multiple write requests for the same object simultaneously, it stores all of the objects.

 For more information about versioning, see [Adding Objects to Versioning Enabled Buckets](https://docs.aws.amazon.com/AmazonS3/latest/dev/AddingObjectstoVersioningEnabledBuckets.html). For information about returning the versioning state of a bucket, see [GetBucketVersioning](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketVersioning.html). 

  **Related Resources** 

 *  [CopyObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CopyObject.html) 


*  [DeleteObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html) 



    """

    Expiration = "Expiration"
    """
     If the expiration is configured for the object (see [PutBucketLifecycleConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketLifecycleConfiguration.html)), the response includes this header. It includes the expiry-date and rule-id key-value pairs that provide information about object expiration. The value of the rule-id is URL encoded.


    """

    ETag = "ETag"
    """
    Entity tag for the uploaded object.


    """

    ServerSideEncryption = "ServerSideEncryption"
    """
    If you specified server-side encryption either with an AWS KMS customer master key (CMK) or Amazon S3-managed encryption key in your PUT request, the response includes this header. It confirms the encryption algorithm that Amazon S3 used to encrypt the object.


    """

    VersionId = "VersionId"
    """
    Version of the object.


    """

    SSECustomerAlgorithm = "SSECustomerAlgorithm"
    """
    If server-side encryption with a customer-provided encryption key was requested, the response will include this header confirming the encryption algorithm used.


    """

    SSECustomerKeyMD5 = "SSECustomerKeyMD5"
    """
    If server-side encryption with a customer-provided encryption key was requested, the response will include this header to provide round-trip message integrity verification of the customer-provided encryption key.


    """

    SSEKMSKeyId = "SSEKMSKeyId"
    """
    If `x-amz-server-side-encryption` is present and has the value of `aws:kms`, this header specifies the ID of the AWS Key Management Service (AWS KMS) symmetric customer managed customer master key (CMK) that was used for the object. 


    """

    SSEKMSEncryptionContext = "SSEKMSEncryptionContext"
    """
    If present, specifies the AWS KMS Encryption Context to use for object encryption. The value of this header is a base64-encoded UTF-8 string holding JSON with the encryption context key-value pairs.


    """

    BucketKeyEnabled = "BucketKeyEnabled"
    """
    Indicates whether the uploaded object uses an S3 Bucket Key for server-side encryption with AWS KMS (SSE-KMS).


    """

    RequestCharged = "RequestCharged"



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


class object_model(Rendered_Resource):
    """

    Removes the null version (if there is one) of an object and inserts a delete marker, which becomes the latest version of the object. If there isn't a null version, Amazon S3 does not remove any objects but will still respond that the command was successful.

 To remove a specific version, you must be the bucket owner and you must use the version Id subresource. Using this subresource permanently deletes the version. If the object deleted is a delete marker, Amazon S3 sets the response header, `x-amz-delete-marker`, to true. 

 If the object you want to delete is in a bucket where the bucket versioning configuration is MFA Delete enabled, you must include the `x-amz-mfa` request header in the DELETE `versionId` request. Requests that include `x-amz-mfa` must use HTTPS. 

  For more information about MFA Delete, see [Using MFA Delete](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMFADelete.html). To see sample requests that use versioning, see [Sample Request](https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectDELETE.html#ExampleVersionObjectDelete). 

 You can delete objects by explicitly calling DELETE Object or configure its lifecycle ([PutBucketLifecycle](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketLifecycle.html)) to enable Amazon S3 to remove them for you. If you want to block users or accounts from removing or deleting objects from your bucket, you must deny them the `s3:DeleteObject`, `s3:DeleteObjectVersion`, and `s3:PutLifeCycleConfiguration` actions. 

 The following action is related to `DeleteObject`:

 *  [PutObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html)
    
    """


    ACL: Optional[Union[ObjectCannedACL, Cloud_Output]] 
    """
    The canned ACL to apply to the object. For more information, see [Canned ACL](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#CannedACL).

 This action is not supported by Amazon S3 on Outposts.
    """


    Body: Optional[Union[bytes, Path, Cloud_Output]]
    """
    Object data.
    """


    Bucket: Union[str, Cloud_Output]
    """
    The bucket name to which the PUT action was initiated. 

 When using this action with an access point, you must direct requests to the access point hostname. The access point hostname takes the form *AccessPointName*-*AccountId*.s3-accesspoint.*Region*.amazonaws.com. When using this action with an access point through the AWS SDKs, you provide the access point ARN in place of the bucket name. For more information about access point ARNs, see [Using access points](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-access-points.html) in the *Amazon S3 User Guide*.

 When using this action with Amazon S3 on Outposts, you must direct requests to the S3 on Outposts hostname. The S3 on Outposts hostname takes the form *AccessPointName*-*AccountId*.*outpostID*.s3-outposts.*Region*.amazonaws.com. When using this action using S3 on Outposts through the AWS SDKs, you provide the Outposts bucket ARN in place of the bucket name. For more information about S3 on Outposts ARNs, see [Using S3 on Outposts](https://docs.aws.amazon.com/AmazonS3/latest/userguide/S3onOutposts.html) in the *Amazon S3 User Guide*.
    """


    CacheControl: Optional[Union[str, Cloud_Output]]
    """
    Can be used to specify caching behavior along the request/reply chain. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.9>.
    """


    ContentDisposition: Optional[Union[str, Cloud_Output]]
    """
    Specifies presentational information for the object. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec19.html#sec19.5.1>.
    """


    ContentEncoding: Optional[Union[str, Cloud_Output]]
    """
    Specifies what content encodings have been applied to the object and thus what decoding mechanisms must be applied to obtain the media-type referenced by the Content-Type header field. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.11>.
    """


    ContentLanguage: Optional[Union[str, Cloud_Output]]
    """
    The language the content is in.
    """


    ContentLength: Optional[Union[int, Cloud_Output]]
    """
    Size of the body in bytes. This parameter is useful when the size of the body cannot be determined automatically. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.13>.
    """


    ContentMD5: Optional[Union[str, Cloud_Output]]
    """
    The base64-encoded 128-bit MD5 digest of the message (without the headers) according to RFC 1864. This header can be used as a message integrity check to verify that the data is the same data that was originally sent. Although it is optional, we recommend using the Content-MD5 mechanism as an end-to-end integrity check. For more information about REST request authentication, see [REST Authentication](https://docs.aws.amazon.com/AmazonS3/latest/dev/RESTAuthentication.html).
    """


    ContentType: Optional[Union[str, Cloud_Output]]
    """
    A standard MIME type describing the format of the contents. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.17>.
    """


    Expires: Optional[Union[str, Cloud_Output]]
    """
    The date and time at which the object is no longer cacheable. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.21>.
    """


    GrantFullControl: Optional[Union[str, Cloud_Output]]
    """
    Gives the grantee READ, READ\_ACP, and WRITE\_ACP permissions on the object.

 This action is not supported by Amazon S3 on Outposts.
    """


    GrantRead: Optional[Union[str, Cloud_Output]]
    """
    Allows grantee to read the object data and its metadata.

 This action is not supported by Amazon S3 on Outposts.
    """


    GrantReadACP: Optional[Union[str, Cloud_Output]]
    """
    Allows grantee to read the object ACL.

 This action is not supported by Amazon S3 on Outposts.
    """


    GrantWriteACP: Optional[Union[str, Cloud_Output]]
    """
    Allows grantee to write the ACL for the applicable object.

 This action is not supported by Amazon S3 on Outposts.
    """


    Key: Union[str, Cloud_Output]
    """
    Object key for which the PUT action was initiated.
    """


    Metadata: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    A map of metadata to store with the object in S3.
    """


    ServerSideEncryption: Optional[Union[ServerSideEncryption, Cloud_Output]] 
    """
    The server-side encryption algorithm used when storing this object in Amazon S3 (for example, AES256, aws:kms).
    """


    StorageClass: Optional[Union[StorageClass, Cloud_Output]] 
    """
    By default, Amazon S3 uses the STANDARD Storage Class to store newly created objects. The STANDARD storage class provides high durability and high availability. Depending on performance needs, you can specify a different Storage Class. Amazon S3 on Outposts only uses the OUTPOSTS Storage Class. For more information, see [Storage Classes](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html) in the *Amazon S3 User Guide*.
    """


    WebsiteRedirectLocation: Optional[Union[str, Cloud_Output]]
    """
    If the bucket is configured as a website, redirects requests for this object to another object in the same bucket or to an external URL. Amazon S3 stores the value of this header in the object metadata. For information about object metadata, see [Object Key and Metadata](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html).

 In the following example, the request header sets the redirect to an object (anotherPage.html) in the same bucket:

  `x-amz-website-redirect-location: /anotherPage.html` 

 In the following example, the request header sets the object redirect to another website:

  `x-amz-website-redirect-location: http://www.example.com/` 

 For more information about website hosting in Amazon S3, see [Hosting Websites on Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html) and [How to Configure Website Page Redirects](https://docs.aws.amazon.com/AmazonS3/latest/dev/how-to-page-redirect.html).
    """


    SSECustomerAlgorithm: Optional[Union[str, Cloud_Output]]
    """
    Specifies the algorithm to use to when encrypting the object (for example, AES256).
    """


    SSECustomerKey: Optional[Union[str, Cloud_Output]]
    """
    Specifies the customer-provided encryption key for Amazon S3 to use in encrypting data. This value is used to store the object and then it is discarded; Amazon S3 does not store the encryption key. The key must be appropriate for use with the algorithm specified in the `x-amz-server-side-encryption-customer-algorithm` header.
    """


    SSECustomerKeyMD5: Optional[Union[str, Cloud_Output]]
    """
    Specifies the 128-bit MD5 digest of the encryption key according to RFC 1321. Amazon S3 uses this header for a message integrity check to ensure that the encryption key was transmitted without error.
    """


    SSEKMSKeyId: Optional[Union[str, Cloud_Output]]
    """
    If `x-amz-server-side-encryption` is present and has the value of `aws:kms`, this header specifies the ID of the AWS Key Management Service (AWS KMS) symmetrical customer managed customer master key (CMK) that was used for the object. If you specify `x-amz-server-side-encryption:aws:kms`, but do not provide `x-amz-server-side-encryption-aws-kms-key-id`, Amazon S3 uses the AWS managed CMK in AWS to protect the data. If the KMS key does not exist in the same account issuing the command, you must use the full ARN and not just the ID.
    """


    SSEKMSEncryptionContext: Optional[Union[str, Cloud_Output]]
    """
    Specifies the AWS KMS Encryption Context to use for object encryption. The value of this header is a base64-encoded UTF-8 string holding JSON with the encryption context key-value pairs.
    """


    BucketKeyEnabled: Optional[Union[bool, Cloud_Output]]
    """
    Specifies whether Amazon S3 should use an S3 Bucket Key for object encryption with server-side encryption using AWS KMS (SSE-KMS). Setting this header to `true` causes Amazon S3 to use an S3 Bucket Key for object encryption with SSE-KMS.

 Specifying this header with a PUT action doesn’t affect bucket-level settings for S3 Bucket Key.
    """


    RequestPayer: Optional[Union[RequestPayer, Cloud_Output]] 


    Tagging: Optional[Union[str, Cloud_Output]]
    """
    The tag-set for the object. The tag-set must be encoded as URL Query parameters. (For example, "Key1=Value1")
    """


    ObjectLockMode: Optional[Union[ObjectLockMode, Cloud_Output]] 
    """
    The Object Lock mode that you want to apply to this object.
    """


    ObjectLockRetainUntilDate: Optional[Union[str, Cloud_Output]]
    """
    The date and time when you want this object's Object Lock to expire. Must be formatted as a timestamp parameter.
    """


    ObjectLockLegalHoldStatus: Optional[Union[ObjectLockLegalHoldStatus, Cloud_Output]] 
    """
    Specifies whether a legal hold will be applied to this object. For more information about S3 Object Lock, see [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/dev/object-lock.html).
    """


    ExpectedBucketOwner: Optional[Union[str, Cloud_Output]]
    """
    The account ID of the expected bucket owner. If the bucket is owned by a different account, the request will fail with an HTTP `403 (Access Denied)` error.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['Bucket', 'Key', 'ACL', 'Body', 'CacheControl', 'ContentDisposition', 'ContentEncoding', 'ContentLanguage', 'ContentLength', 'ContentMD5', 'ContentType', 'Expires', 'GrantFullControl', 'GrantRead', 'GrantReadACP', 'GrantWriteACP', 'Metadata', 'ServerSideEncryption', 'StorageClass', 'WebsiteRedirectLocation', 'SSECustomerAlgorithm', 'SSECustomerKey', 'SSECustomerKeyMD5', 'SSEKMSKeyId', 'SSEKMSEncryptionContext', 'BucketKeyEnabled', 'RequestPayer', 'Tagging', 'ObjectLockMode', 'ObjectLockRetainUntilDate', 'ObjectLockLegalHoldStatus', 'ExpectedBucketOwner'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['Bucket', 'Key', 'MFA', 'VersionId', 'RequestPayer', 'BypassGovernanceRetention', 'ExpectedBucketOwner'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


