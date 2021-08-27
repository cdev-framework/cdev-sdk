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

    def __init__(self, cdev_name: str, Bucket: str, ACL: BucketCannedACL=None, CreateBucketConfiguration: CreateBucketConfiguration=None, GrantFullControl: str=None, GrantRead: str=None, GrantReadACP: str=None, GrantWrite: str=None, GrantWriteACP: str=None, ObjectLockEnabledForBucket: bool=None):
        ""
        super().__init__(cdev_name)

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


class Object(Cdev_Resource):
    """
    Removes the null version (if there is one) of an object and inserts a delete marker, which becomes the latest version of the object. If there isn't a null version, Amazon S3 does not remove any objects but will still respond that the command was successful.

 To remove a specific version, you must be the bucket owner and you must use the version Id subresource. Using this subresource permanently deletes the version. If the object deleted is a delete marker, Amazon S3 sets the response header, `x-amz-delete-marker`, to true. 

 If the object you want to delete is in a bucket where the bucket versioning configuration is MFA Delete enabled, you must include the `x-amz-mfa` request header in the DELETE `versionId` request. Requests that include `x-amz-mfa` must use HTTPS. 

  For more information about MFA Delete, see [Using MFA Delete](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMFADelete.html). To see sample requests that use versioning, see [Sample Request](https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectDELETE.html#ExampleVersionObjectDelete). 

 You can delete objects by explicitly calling DELETE Object or configure its lifecycle ([PutBucketLifecycle](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketLifecycle.html)) to enable Amazon S3 to remove them for you. If you want to block users or accounts from removing or deleting objects from your bucket, you must deny them the `s3:DeleteObject`, `s3:DeleteObjectVersion`, and `s3:PutLifeCycleConfiguration` actions. 

 The following action is related to `DeleteObject`:

 *  [PutObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html) 



    """

    def __init__(self, cdev_name: str, Bucket: str, Key: str, ACL: ObjectCannedACL=None, Body: bytes=None, CacheControl: str=None, ContentDisposition: str=None, ContentEncoding: str=None, ContentLanguage: str=None, ContentLength: int=None, ContentMD5: str=None, ContentType: str=None, Expires: str=None, GrantFullControl: str=None, GrantRead: str=None, GrantReadACP: str=None, GrantWriteACP: str=None, Metadata: Dict[str, str]=None, ServerSideEncryption: ServerSideEncryption=None, StorageClass: StorageClass=None, WebsiteRedirectLocation: str=None, SSECustomerAlgorithm: str=None, SSECustomerKey: str=None, SSECustomerKeyMD5: str=None, SSEKMSKeyId: str=None, SSEKMSEncryptionContext: str=None, BucketKeyEnabled: bool=None, RequestPayer: RequestPayer=None, Tagging: str=None, ObjectLockMode: ObjectLockMode=None, ObjectLockRetainUntilDate: str=None, ObjectLockLegalHoldStatus: ObjectLockLegalHoldStatus=None, ExpectedBucketOwner: str=None):
        ""
        super().__init__(cdev_name)

        self.ACL = ACL
        """
        The canned ACL to apply to the object. For more information, see [Canned ACL](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#CannedACL).

 This action is not supported by Amazon S3 on Outposts.


        """

        self.Body = Body
        """
        Object data.


        """

        self.Bucket = Bucket
        """
        The bucket name to which the PUT action was initiated. 

 When using this action with an access point, you must direct requests to the access point hostname. The access point hostname takes the form *AccessPointName*-*AccountId*.s3-accesspoint.*Region*.amazonaws.com. When using this action with an access point through the AWS SDKs, you provide the access point ARN in place of the bucket name. For more information about access point ARNs, see [Using access points](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-access-points.html) in the *Amazon S3 User Guide*.

 When using this action with Amazon S3 on Outposts, you must direct requests to the S3 on Outposts hostname. The S3 on Outposts hostname takes the form *AccessPointName*-*AccountId*.*outpostID*.s3-outposts.*Region*.amazonaws.com. When using this action using S3 on Outposts through the AWS SDKs, you provide the Outposts bucket ARN in place of the bucket name. For more information about S3 on Outposts ARNs, see [Using S3 on Outposts](https://docs.aws.amazon.com/AmazonS3/latest/userguide/S3onOutposts.html) in the *Amazon S3 User Guide*.


        """

        self.CacheControl = CacheControl
        """
         Can be used to specify caching behavior along the request/reply chain. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.9>.


        """

        self.ContentDisposition = ContentDisposition
        """
        Specifies presentational information for the object. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec19.html#sec19.5.1>.


        """

        self.ContentEncoding = ContentEncoding
        """
        Specifies what content encodings have been applied to the object and thus what decoding mechanisms must be applied to obtain the media-type referenced by the Content-Type header field. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.11>.


        """

        self.ContentLanguage = ContentLanguage
        """
        The language the content is in.


        """

        self.ContentLength = ContentLength
        """
        Size of the body in bytes. This parameter is useful when the size of the body cannot be determined automatically. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.13>.


        """

        self.ContentMD5 = ContentMD5
        """
        The base64-encoded 128-bit MD5 digest of the message (without the headers) according to RFC 1864. This header can be used as a message integrity check to verify that the data is the same data that was originally sent. Although it is optional, we recommend using the Content-MD5 mechanism as an end-to-end integrity check. For more information about REST request authentication, see [REST Authentication](https://docs.aws.amazon.com/AmazonS3/latest/dev/RESTAuthentication.html).


        """

        self.ContentType = ContentType
        """
        A standard MIME type describing the format of the contents. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.17>.


        """

        self.Expires = Expires
        """
        The date and time at which the object is no longer cacheable. For more information, see <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.21>.


        """

        self.GrantFullControl = GrantFullControl
        """
        Gives the grantee READ, READ\_ACP, and WRITE\_ACP permissions on the object.

 This action is not supported by Amazon S3 on Outposts.


        """

        self.GrantRead = GrantRead
        """
        Allows grantee to read the object data and its metadata.

 This action is not supported by Amazon S3 on Outposts.


        """

        self.GrantReadACP = GrantReadACP
        """
        Allows grantee to read the object ACL.

 This action is not supported by Amazon S3 on Outposts.


        """

        self.GrantWriteACP = GrantWriteACP
        """
        Allows grantee to write the ACL for the applicable object.

 This action is not supported by Amazon S3 on Outposts.


        """

        self.Key = Key
        """
        Object key for which the PUT action was initiated.


        """

        self.Metadata = Metadata
        """
        A map of metadata to store with the object in S3.


        """

        self.ServerSideEncryption = ServerSideEncryption
        """
        The server-side encryption algorithm used when storing this object in Amazon S3 (for example, AES256, aws:kms).


        """

        self.StorageClass = StorageClass
        """
        By default, Amazon S3 uses the STANDARD Storage Class to store newly created objects. The STANDARD storage class provides high durability and high availability. Depending on performance needs, you can specify a different Storage Class. Amazon S3 on Outposts only uses the OUTPOSTS Storage Class. For more information, see [Storage Classes](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html) in the *Amazon S3 User Guide*.


        """

        self.WebsiteRedirectLocation = WebsiteRedirectLocation
        """
        If the bucket is configured as a website, redirects requests for this object to another object in the same bucket or to an external URL. Amazon S3 stores the value of this header in the object metadata. For information about object metadata, see [Object Key and Metadata](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html).

 In the following example, the request header sets the redirect to an object (anotherPage.html) in the same bucket:

  `x-amz-website-redirect-location: /anotherPage.html` 

 In the following example, the request header sets the object redirect to another website:

  `x-amz-website-redirect-location: http://www.example.com/` 

 For more information about website hosting in Amazon S3, see [Hosting Websites on Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html) and [How to Configure Website Page Redirects](https://docs.aws.amazon.com/AmazonS3/latest/dev/how-to-page-redirect.html). 


        """

        self.SSECustomerAlgorithm = SSECustomerAlgorithm
        """
        Specifies the algorithm to use to when encrypting the object (for example, AES256).


        """

        self.SSECustomerKey = SSECustomerKey
        """
        Specifies the customer-provided encryption key for Amazon S3 to use in encrypting data. This value is used to store the object and then it is discarded; Amazon S3 does not store the encryption key. The key must be appropriate for use with the algorithm specified in the `x-amz-server-side-encryption-customer-algorithm` header.


        """

        self.SSECustomerKeyMD5 = SSECustomerKeyMD5
        """
        Specifies the 128-bit MD5 digest of the encryption key according to RFC 1321. Amazon S3 uses this header for a message integrity check to ensure that the encryption key was transmitted without error.


        """

        self.SSEKMSKeyId = SSEKMSKeyId
        """
        If `x-amz-server-side-encryption` is present and has the value of `aws:kms`, this header specifies the ID of the AWS Key Management Service (AWS KMS) symmetrical customer managed customer master key (CMK) that was used for the object. If you specify `x-amz-server-side-encryption:aws:kms`, but do not provide `x-amz-server-side-encryption-aws-kms-key-id`, Amazon S3 uses the AWS managed CMK in AWS to protect the data. If the KMS key does not exist in the same account issuing the command, you must use the full ARN and not just the ID. 


        """

        self.SSEKMSEncryptionContext = SSEKMSEncryptionContext
        """
        Specifies the AWS KMS Encryption Context to use for object encryption. The value of this header is a base64-encoded UTF-8 string holding JSON with the encryption context key-value pairs.


        """

        self.BucketKeyEnabled = BucketKeyEnabled
        """
        Specifies whether Amazon S3 should use an S3 Bucket Key for object encryption with server-side encryption using AWS KMS (SSE-KMS). Setting this header to `true` causes Amazon S3 to use an S3 Bucket Key for object encryption with SSE-KMS.

 Specifying this header with a PUT action doesn’t affect bucket-level settings for S3 Bucket Key.


        """

        self.RequestPayer = RequestPayer

        self.Tagging = Tagging
        """
        The tag-set for the object. The tag-set must be encoded as URL Query parameters. (For example, "Key1=Value1")


        """

        self.ObjectLockMode = ObjectLockMode
        """
        The Object Lock mode that you want to apply to this object.


        """

        self.ObjectLockRetainUntilDate = ObjectLockRetainUntilDate
        """
        The date and time when you want this object's Object Lock to expire. Must be formatted as a timestamp parameter.


        """

        self.ObjectLockLegalHoldStatus = ObjectLockLegalHoldStatus
        """
        Specifies whether a legal hold will be applied to this object. For more information about S3 Object Lock, see [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/dev/object-lock.html).


        """

        self.ExpectedBucketOwner = ExpectedBucketOwner
        """
        The account ID of the expected bucket owner. If the bucket is owned by a different account, the request will fail with an HTTP `403 (Access Denied)` error.


        """

        self.hash = hasher.hash_list([self.Bucket, self.Key, self.ACL, self.Body, self.CacheControl, self.ContentDisposition, self.ContentEncoding, self.ContentLanguage, self.ContentLength, self.ContentMD5, self.ContentType, self.Expires, self.GrantFullControl, self.GrantRead, self.GrantReadACP, self.GrantWriteACP, self.Metadata, self.ServerSideEncryption, self.StorageClass, self.WebsiteRedirectLocation, self.SSECustomerAlgorithm, self.SSECustomerKey, self.SSECustomerKeyMD5, self.SSEKMSKeyId, self.SSEKMSEncryptionContext, self.BucketKeyEnabled, self.RequestPayer, self.Tagging, self.ObjectLockMode, self.ObjectLockRetainUntilDate, self.ObjectLockLegalHoldStatus, self.ExpectedBucketOwner])

    def render(self) -> object_model:
        data = {
            "ruuid": "cdev::aws::s3::object",
            "name": self.name,
            "hash": self.hash,
            "ACL": self.ACL,
            "Body": self.Body,
            "Bucket": self.Bucket,
            "CacheControl": self.CacheControl,
            "ContentDisposition": self.ContentDisposition,
            "ContentEncoding": self.ContentEncoding,
            "ContentLanguage": self.ContentLanguage,
            "ContentLength": self.ContentLength,
            "ContentMD5": self.ContentMD5,
            "ContentType": self.ContentType,
            "Expires": self.Expires,
            "GrantFullControl": self.GrantFullControl,
            "GrantRead": self.GrantRead,
            "GrantReadACP": self.GrantReadACP,
            "GrantWriteACP": self.GrantWriteACP,
            "Key": self.Key,
            "Metadata": self.Metadata,
            "ServerSideEncryption": self.ServerSideEncryption,
            "StorageClass": self.StorageClass,
            "WebsiteRedirectLocation": self.WebsiteRedirectLocation,
            "SSECustomerAlgorithm": self.SSECustomerAlgorithm,
            "SSECustomerKey": self.SSECustomerKey,
            "SSECustomerKeyMD5": self.SSECustomerKeyMD5,
            "SSEKMSKeyId": self.SSEKMSKeyId,
            "SSEKMSEncryptionContext": self.SSEKMSEncryptionContext,
            "BucketKeyEnabled": self.BucketKeyEnabled,
            "RequestPayer": self.RequestPayer,
            "Tagging": self.Tagging,
            "ObjectLockMode": self.ObjectLockMode,
            "ObjectLockRetainUntilDate": self.ObjectLockRetainUntilDate,
            "ObjectLockLegalHoldStatus": self.ObjectLockLegalHoldStatus,
            "ExpectedBucketOwner": self.ExpectedBucketOwner,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return object_model(**filtered_data)

    def from_output(self, key: object_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::s3::object::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::s3::object::{self.hash}", "key": key, "type": "cdev_output"})


class s3_object(BaseModel):
    S3Bucket: str
    S3Key: str