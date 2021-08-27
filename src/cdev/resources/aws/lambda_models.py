from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Dict, Union, Dict

from ...models import Cloud_Output, Rendered_Resource

from ...backend import cloud_mapper_manager


class Runtime(str, Enum): 


    nodejs = 'nodejs'
    
    nodejs4_3 = 'nodejs4.3'
    
    nodejs6_10 = 'nodejs6.10'
    
    nodejs8_10 = 'nodejs8.10'
    
    nodejs10_x = 'nodejs10.x'
    
    nodejs12_x = 'nodejs12.x'
    
    nodejs14_x = 'nodejs14.x'
    
    java8 = 'java8'
    
    java8_al2 = 'java8.al2'
    
    java11 = 'java11'
    
    python2_7 = 'python2.7'
    
    python3_6 = 'python3.6'
    
    python3_7 = 'python3.7'
    
    python3_8 = 'python3.8'
    
    dotnetcore1_0 = 'dotnetcore1.0'
    
    dotnetcore2_0 = 'dotnetcore2.0'
    
    dotnetcore2_1 = 'dotnetcore2.1'
    
    dotnetcore3_1 = 'dotnetcore3.1'
    
    nodejs4_3_edge = 'nodejs4.3-edge'
    
    go1_x = 'go1.x'
    
    ruby2_5 = 'ruby2.5'
    
    ruby2_7 = 'ruby2.7'
    
    provided = 'provided'
    
    provided_al2 = 'provided.al2'
    







class FunctionCode(BaseModel):
    """
    The code for the Lambda function. You can specify either an object in Amazon S3, upload a .zip file archive deployment package directly, or specify the URI of a container image.


    """


    ZipFile: Union[bytes, Cloud_Output]
    """
    The base64-encoded contents of the deployment package. Amazon Web Services SDK and Amazon Web Services CLI clients handle the encoding for you.


    """

    S3Bucket: Union[str, Cloud_Output]
    """
    An Amazon S3 bucket in the same Amazon Web Services Region as your function. The bucket can be in a different Amazon Web Services account.


    """

    S3Key: Union[str, Cloud_Output]
    """
    The Amazon S3 key of the deployment package.


    """

    S3ObjectVersion: Union[str, Cloud_Output]
    """
    For versioned objects, the version of the deployment package object to use.


    """

    ImageUri: Union[str, Cloud_Output]
    """
    URI of a [container image](https://docs.aws.amazon.com/lambda/latest/dg/lambda-images.html) in the Amazon ECR registry.


    """


    def __init__(self, ZipFile: bytes, S3Bucket: str, S3Key: str, S3ObjectVersion: str, ImageUri: str ):
        "My doc string"
        super().__init__(**{
            "ZipFile": ZipFile,
            "S3Bucket": S3Bucket,
            "S3Key": S3Key,
            "S3ObjectVersion": S3ObjectVersion,
            "ImageUri": ImageUri,
        })        






class VpcConfig(BaseModel):
    """
    The VPC security groups and subnets that are attached to a Lambda function. For more information, see [VPC Settings](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html).


    """


    SubnetIds: Union[List[str], Cloud_Output]

    SecurityGroupIds: Union[List[str], Cloud_Output]


    def __init__(self, SubnetIds: List[str], SecurityGroupIds: List[str] ):
        "My doc string"
        super().__init__(**{
            "SubnetIds": SubnetIds,
            "SecurityGroupIds": SecurityGroupIds,
        })        



class PackageType(str, Enum): 


    Zip = 'Zip'
    
    Image = 'Image'
    


class DeadLetterConfig(BaseModel):
    """
    The [dead-letter queue](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html#dlq) for failed asynchronous invocations.


    """


    TargetArn: Union[str, Cloud_Output]
    """
    The Amazon Resource Name (ARN) of an Amazon SQS queue or Amazon SNS topic.


    """


    def __init__(self, TargetArn: str ):
        "My doc string"
        super().__init__(**{
            "TargetArn": TargetArn,
        })        





class Environment(BaseModel):
    """
    A function's environment variable settings. You can use environment variables to adjust your function's behavior without updating code. An environment variable is a pair of strings that are stored in a function's version-specific configuration. 


    """


    Variables: Dict[str, str]
    """
    Environment variable key-value pairs. For more information, see [Using Lambda environment variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html).


    """


    def __init__(self, Variables: Dict ):
        "My doc string"
        super().__init__(**{
            "Variables": Variables,
        })        




class TracingMode(str, Enum): 


    Active = 'Active'
    
    PassThrough = 'PassThrough'
    

class TracingConfig(BaseModel):
    """
    The function's [X-Ray](https://docs.aws.amazon.com/lambda/latest/dg/services-xray.html) tracing configuration. To sample and record incoming requests, set `Mode` to `Active`.


    """


    Mode: Union[TracingMode, Cloud_Output]
    """
    The tracing mode.


    """


    def __init__(self, Mode: TracingMode ):
        "My doc string"
        super().__init__(**{
            "Mode": Mode,
        })        








class FileSystemConfig(BaseModel):
    """
    Details about the connection between a Lambda function and an [Amazon EFS file system](https://docs.aws.amazon.com/lambda/latest/dg/configuration-filesystem.html).


    """


    Arn: Union[str, Cloud_Output]
    """
    The Amazon Resource Name (ARN) of the Amazon EFS access point that provides access to the file system.


    """

    LocalMountPath: Union[str, Cloud_Output]
    """
    The path where the function can access the file system, starting with `/mnt/`.


    """


    def __init__(self, Arn: str, LocalMountPath: str ):
        "My doc string"
        super().__init__(**{
            "Arn": Arn,
            "LocalMountPath": LocalMountPath,
        })        




class ImageConfig(BaseModel):
    """
    Configuration values that override the container image Dockerfile settings. See [Container settings](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html#images-parms). 


    """


    EntryPoint: Union[List[str], Cloud_Output]
    """
    URI of a [container image](https://docs.aws.amazon.com/lambda/latest/dg/lambda-images.html) in the Amazon ECR registry.


    """

    Command: Union[List[str], Cloud_Output]
    """
    URI of a [container image](https://docs.aws.amazon.com/lambda/latest/dg/lambda-images.html) in the Amazon ECR registry.


    """

    WorkingDirectory: Union[str, Cloud_Output]
    """
    Specifies the working directory.


    """


    def __init__(self, EntryPoint: List[str], Command: List[str], WorkingDirectory: str ):
        "My doc string"
        super().__init__(**{
            "EntryPoint": EntryPoint,
            "Command": Command,
            "WorkingDirectory": WorkingDirectory,
        })        






class lambdafunction_output(str, Enum):
    """
    Creates a Lambda function. To create a function, you need a [deployment package](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html) and an [execution role](https://docs.aws.amazon.com/lambda/latest/dg/intro-permission-model.html#lambda-intro-execution-role). The deployment package is a .zip file archive or container image that contains your function code. The execution role grants the function permission to use Amazon Web Services services, such as Amazon CloudWatch Logs for log streaming and X-Ray for request tracing.

 You set the package type to `Image` if the deployment package is a [container image](https://docs.aws.amazon.com/lambda/latest/dg/lambda-images.html). For a container image, the code property must include the URI of a container image in the Amazon ECR registry. You do not need to specify the handler and runtime properties. 

 You set the package type to `Zip` if the deployment package is a [.zip file archive](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html#gettingstarted-package-zip). For a .zip file archive, the code property specifies the location of the .zip file. You must also specify the handler and runtime properties.

 When you create a function, Lambda provisions an instance of the function and its supporting resources. If your function connects to a VPC, this process can take a minute or so. During this time, you can't invoke or modify the function. The `State`, `StateReason`, and `StateReasonCode` fields in the response from GetFunctionConfiguration indicate when the function is ready to invoke. For more information, see [Function States](https://docs.aws.amazon.com/lambda/latest/dg/functions-states.html).

 A function has an unpublished version, and can have published versions and aliases. The unpublished version changes when you update your function's code and configuration. A published version is a snapshot of your function code and configuration that can't be changed. An alias is a named resource that maps to a version, and can be changed to map to a different version. Use the `Publish` parameter to create version `1` of your function from its initial configuration.

 The other parameters let you configure version-specific and function-level settings. You can modify version-specific settings later with UpdateFunctionConfiguration. Function-level settings apply to both the unpublished and published versions of the function, and include tags (TagResource) and per-function concurrency limits (PutFunctionConcurrency).

 You can use code signing if your deployment package is a .zip file archive. To enable code signing for this function, specify the ARN of a code-signing configuration. When a user attempts to deploy a code package with UpdateFunctionCode, Lambda checks that the code package has a valid signature from a trusted publisher. The code-signing configuration includes set set of signing profiles, which define the trusted publishers for this function.

 If another account or an Amazon Web Services service invokes your function, use AddPermission to grant permission by creating a resource-based IAM policy. You can grant permissions at the function level, on a version, or on an alias.

 To invoke your function directly, use Invoke. To invoke your function in response to events in other Amazon Web Services services, create an event source mapping (CreateEventSourceMapping), or configure a function trigger in the other service. For more information, see [Invoking Functions](https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html).


    """

    FunctionName = "FunctionName"
    """
    The name of the function.


    """

    FunctionArn = "FunctionArn"
    """
    The function's Amazon Resource Name (ARN).


    """

    Runtime = "Runtime"
    """
    The runtime environment for the Lambda function.


    """

    Role = "Role"
    """
    The function's execution role.


    """

    Handler = "Handler"
    """
    The function that Lambda calls to begin executing your function.


    """

    CodeSize = "CodeSize"
    """
    The size of the function's deployment package, in bytes.


    """

    Description = "Description"
    """
    The function's description.


    """

    Timeout = "Timeout"
    """
    The amount of time in seconds that Lambda allows a function to run before stopping it.


    """

    MemorySize = "MemorySize"
    """
    The amount of memory available to the function at runtime. 


    """

    LastModified = "LastModified"
    """
    The date and time that the function was last updated, in [ISO-8601 format](https://www.w3.org/TR/NOTE-datetime) (YYYY-MM-DDThh:mm:ss.sTZD).


    """

    CodeSha256 = "CodeSha256"
    """
    The SHA256 hash of the function's deployment package.


    """

    Version = "Version"
    """
    The version of the Lambda function.


    """

    VpcConfig = "VpcConfig"
    """
    The function's networking configuration.


    """

    DeadLetterConfig = "DeadLetterConfig"
    """
    The function's dead letter queue.


    """

    Environment = "Environment"
    """
    The function's [environment variables](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html).


    """

    KMSKeyArn = "KMSKeyArn"
    """
    The KMS key that's used to encrypt the function's environment variables. This key is only returned if you've configured a customer managed CMK.


    """

    TracingConfig = "TracingConfig"
    """
    The function's X-Ray tracing configuration.


    """

    MasterArn = "MasterArn"
    """
    For Lambda@Edge functions, the ARN of the master function.


    """

    RevisionId = "RevisionId"
    """
    The latest updated revision of the function or alias.


    """

    Layers = "Layers"
    """
    The function's  [layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html).


    """

    State = "State"
    """
    The current state of the function. When the state is `Inactive`, you can reactivate the function by invoking it.


    """

    StateReason = "StateReason"
    """
    The reason for the function's current state.


    """

    StateReasonCode = "StateReasonCode"
    """
    The reason code for the function's current state. When the code is `Creating`, you can't invoke or modify the function.


    """

    LastUpdateStatus = "LastUpdateStatus"
    """
    The status of the last update that was performed on the function. This is first set to `Successful` after function creation completes.


    """

    LastUpdateStatusReason = "LastUpdateStatusReason"
    """
    The reason for the last update that was performed on the function.


    """

    LastUpdateStatusReasonCode = "LastUpdateStatusReasonCode"
    """
    The reason code for the last update that was performed on the function.


    """

    FileSystemConfigs = "FileSystemConfigs"
    """
    Connection settings for an [Amazon EFS file system](https://docs.aws.amazon.com/lambda/latest/dg/configuration-filesystem.html).


    """

    PackageType = "PackageType"
    """
    The type of deployment package. Set to `Image` for container image and set `Zip` for .zip file archive.


    """

    ImageConfigResponse = "ImageConfigResponse"
    """
    The function's image configuration values.


    """

    SigningProfileVersionArn = "SigningProfileVersionArn"
    """
    The ARN of the signing profile version.


    """

    SigningJobArn = "SigningJobArn"
    """
    The ARN of the signing job.


    """



class lambdafunction_model(Rendered_Resource):
    """

    Deletes a Lambda function. To delete a specific function version, use the `Qualifier` parameter. Otherwise, all versions and aliases are deleted.

 To delete Lambda event source mappings that invoke a function, use DeleteEventSourceMapping. For Amazon Web Services services and resources that invoke your function directly, delete the trigger in the service where you originally configured it.
    
    """


    FunctionName: Union[str, Cloud_Output]
    """
    The name of the Lambda function.

  **Name formats** 

 *  **Function name** - `my-function`.


*  **Function ARN** - `arn:aws:lambda:us-west-2:123456789012:function:my-function`.


*  **Partial ARN** - `123456789012:function:my-function`.



 The length constraint applies only to the full ARN. If you specify only the function name, it is limited to 64 characters in length.
    """


    Runtime: Optional[Union[Runtime, Cloud_Output]] 
    """
    The identifier of the function's [runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html).
    """


    Role: Union[str, Cloud_Output]
    """
    The Amazon Resource Name (ARN) of the function's execution role.
    """


    Handler: Optional[Union[str, Cloud_Output]]
    """
    The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see [Programming Model](https://docs.aws.amazon.com/lambda/latest/dg/programming-model-v2.html).
    """


    Code: Union[FunctionCode, Cloud_Output] 
    """
    The code for the function.
    """


    Description: Optional[Union[str, Cloud_Output]]
    """
    A description of the function.
    """


    Timeout: Optional[Union[int, Cloud_Output]]
    """
    The amount of time that Lambda allows a function to run before stopping it. The default is 3 seconds. The maximum allowed value is 900 seconds. For additional information, see [Lambda execution environment](https://docs.aws.amazon.com/lambda/latest/dg/runtimes-context.html).
    """


    MemorySize: Optional[Union[int, Cloud_Output]]
    """
    The amount of [memory available to the function](https://docs.aws.amazon.com/lambda/latest/dg/configuration-memory.html) at runtime. Increasing the function memory also increases its CPU allocation. The default value is 128 MB. The value can be any multiple of 1 MB.
    """


    Publish: Optional[Union[bool, Cloud_Output]]
    """
    Set to true to publish the first version of the function during creation.
    """


    VpcConfig: Optional[Union[VpcConfig, Cloud_Output]] 
    """
    For network connectivity to Amazon Web Services resources in a VPC, specify a list of security groups and subnets in the VPC. When you connect a function to a VPC, it can only access resources and the internet through that VPC. For more information, see [VPC Settings](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html).
    """


    PackageType: Optional[Union[PackageType, Cloud_Output]] 
    """
    The type of deployment package. Set to `Image` for container image and set `Zip` for ZIP archive.
    """


    DeadLetterConfig: Optional[Union[DeadLetterConfig, Cloud_Output]] 
    """
    A dead letter queue configuration that specifies the queue or topic where Lambda sends asynchronous events when they fail processing. For more information, see [Dead Letter Queues](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html#dlq).
    """


    Environment: Optional[Union[Environment, Cloud_Output]] 
    """
    Environment variables that are accessible from function code during execution.
    """


    KMSKeyArn: Optional[Union[str, Cloud_Output]]
    """
    The ARN of the Amazon Web Services Key Management Service (KMS) key that's used to encrypt your function's environment variables. If it's not provided, Lambda uses a default service key.
    """


    TracingConfig: Optional[Union[TracingConfig, Cloud_Output]] 
    """
    Set `Mode` to `Active` to sample and trace a subset of incoming requests with [X-Ray](https://docs.aws.amazon.com/lambda/latest/dg/services-xray.html).
    """


    Tags: Optional[Union[Dict[str,str], Cloud_Output]]
    """
    A list of [tags](https://docs.aws.amazon.com/lambda/latest/dg/tagging.html) to apply to the function.
    """


    Layers: Optional[Union[List[str], Cloud_Output]]


    FileSystemConfigs: Optional[Union[List[FileSystemConfig], Cloud_Output]]
    """
    Details about the connection between a Lambda function and an [Amazon EFS file system](https://docs.aws.amazon.com/lambda/latest/dg/configuration-filesystem.html).
    """


    ImageConfig: Optional[Union[ImageConfig, Cloud_Output]] 
    """
    Container image [configuration values](https://docs.aws.amazon.com/lambda/latest/dg/configuration-images.html#configuration-images-settings) that override the values in the container image Dockerfile.
    """


    CodeSigningConfigArn: Optional[Union[str, Cloud_Output]]
    """
    To enable code signing for this function, specify the ARN of a code-signing configuration. A code-signing configuration includes a set of signing profiles, which define the trusted publishers for this function.
    """



    def filter_to_create(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['FunctionName', 'Role', 'Code', 'Runtime', 'Handler', 'Description', 'Timeout', 'MemorySize', 'Publish', 'VpcConfig', 'PackageType', 'DeadLetterConfig', 'Environment', 'KMSKeyArn', 'TracingConfig', 'Tags', 'Layers', 'FileSystemConfigs', 'ImageConfig', 'CodeSigningConfigArn'])

        return {k:v for k,v in self.dict().items() if k in NEEDED_ATTRIBUTES and v}

    def filter_to_remove(self, identifier) -> dict:
        NEEDED_ATTRIBUTES = set(['FunctionName', 'Qualifier'])
        return {(k if type(k)==str else k[0]):(cloud_mapper_manager.get_output_value(identifier, k) if type(k)==str else cloud_mapper_manager.get_output_value(identifier, k[1])) for k in NEEDED_ATTRIBUTES }

    class Config:
        extra='ignore'


