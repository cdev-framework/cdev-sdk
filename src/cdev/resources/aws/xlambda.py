from pydantic.main import BaseModel
from enum import Enum
from typing import List, Optional, Callable, Any
from pathlib import Path


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .lambda_models import *


class LambdaFunction(Cdev_Resource):
    """
    Deletes a Lambda function. To delete a specific function version, use the `Qualifier` parameter. Otherwise, all versions and aliases are deleted.

 To delete Lambda event source mappings that invoke a function, use DeleteEventSourceMapping. For Amazon Web Services services and resources that invoke your function directly, delete the trigger in the service where you originally configured it.


    """

    def __init__(self, cdev_name: str, FunctionName: str, Role: str, Code: FunctionCode, Runtime: Runtime=None, Handler: str=None, Description: str=None, Timeout: int=None, MemorySize: int=None, Publish: bool=None, VpcConfig: VpcConfig=None, PackageType: PackageType=None, DeadLetterConfig: DeadLetterConfig=None, Environment: Environment=None, KMSKeyArn: str=None, TracingConfig: TracingConfig=None, Tags: Dict[str, str]=None, Layers: List[str]=None, FileSystemConfigs: List[FileSystemConfig]=None, ImageConfig: ImageConfig=None, CodeSigningConfigArn: str=None):
        ""
        super().__init__(cdev_name)

        self.FunctionName = FunctionName
        """
        The name of the Lambda function.

  **Name formats** 

 *  **Function name** - `my-function`.


*  **Function ARN** - `arn:aws:lambda:us-west-2:123456789012:function:my-function`.


*  **Partial ARN** - `123456789012:function:my-function`.



 The length constraint applies only to the full ARN. If you specify only the function name, it is limited to 64 characters in length.


        """

        self.Runtime = Runtime
        """
        The identifier of the function's [runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html).


        """

        self.Role = Role
        """
        The Amazon Resource Name (ARN) of the function's execution role.


        """

        self.Handler = Handler
        """
        The name of the method within your code that Lambda calls to execute your function. The format includes the file name. It can also include namespaces and other qualifiers, depending on the runtime. For more information, see [Programming Model](https://docs.aws.amazon.com/lambda/latest/dg/programming-model-v2.html).


        """

        self.Code = Code
        """
        The code for the function.


        """

        self.Description = Description
        """
        A description of the function.


        """

        self.Timeout = Timeout
        """
        The amount of time that Lambda allows a function to run before stopping it. The default is 3 seconds. The maximum allowed value is 900 seconds. For additional information, see [Lambda execution environment](https://docs.aws.amazon.com/lambda/latest/dg/runtimes-context.html).


        """

        self.MemorySize = MemorySize
        """
        The amount of [memory available to the function](https://docs.aws.amazon.com/lambda/latest/dg/configuration-memory.html) at runtime. Increasing the function memory also increases its CPU allocation. The default value is 128 MB. The value can be any multiple of 1 MB.


        """

        self.Publish = Publish
        """
        Set to true to publish the first version of the function during creation.


        """

        self.VpcConfig = VpcConfig
        """
        For network connectivity to Amazon Web Services resources in a VPC, specify a list of security groups and subnets in the VPC. When you connect a function to a VPC, it can only access resources and the internet through that VPC. For more information, see [VPC Settings](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html).


        """

        self.PackageType = PackageType
        """
        The type of deployment package. Set to `Image` for container image and set `Zip` for ZIP archive.


        """

        self.DeadLetterConfig = DeadLetterConfig
        """
        A dead letter queue configuration that specifies the queue or topic where Lambda sends asynchronous events when they fail processing. For more information, see [Dead Letter Queues](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html#dlq).


        """

        self.Environment = Environment
        """
        Environment variables that are accessible from function code during execution.


        """

        self.KMSKeyArn = KMSKeyArn
        """
        The ARN of the Amazon Web Services Key Management Service (KMS) key that's used to encrypt your function's environment variables. If it's not provided, Lambda uses a default service key.


        """

        self.TracingConfig = TracingConfig
        """
        Set `Mode` to `Active` to sample and trace a subset of incoming requests with [X-Ray](https://docs.aws.amazon.com/lambda/latest/dg/services-xray.html).


        """

        self.Tags = Tags
        """
        A list of [tags](https://docs.aws.amazon.com/lambda/latest/dg/tagging.html) to apply to the function.


        """

        self.Layers = Layers

        self.FileSystemConfigs = FileSystemConfigs
        """
        Details about the connection between a Lambda function and an [Amazon EFS file system](https://docs.aws.amazon.com/lambda/latest/dg/configuration-filesystem.html).


        """

        self.ImageConfig = ImageConfig
        """
        Container image [configuration values](https://docs.aws.amazon.com/lambda/latest/dg/configuration-images.html#configuration-images-settings) that override the values in the container image Dockerfile.


        """

        self.CodeSigningConfigArn = CodeSigningConfigArn
        """
        To enable code signing for this function, specify the ARN of a code-signing configuration. A code-signing configuration includes a set of signing profiles, which define the trusted publishers for this function.


        """

        self.hash = hasher.hash_list([self.FunctionName, self.Role, self.Code, self.Runtime, self.Handler, self.Description, self.Timeout, self.MemorySize, self.Publish, self.VpcConfig, self.PackageType, self.DeadLetterConfig, self.Environment, self.KMSKeyArn, self.TracingConfig, self.Tags, self.Layers, self.FileSystemConfigs, self.ImageConfig, self.CodeSigningConfigArn])

    def render(self) -> lambdafunction_model:
        data = {
            "ruuid": "cdev::aws::lambda::function",
            "name": self.name,
            "hash": self.hash,
            "FunctionName": self.FunctionName,
            "Runtime": self.Runtime,
            "Role": self.Role,
            "Handler": self.Handler,
            "Code": self.Code,
            "Description": self.Description,
            "Timeout": self.Timeout,
            "MemorySize": self.MemorySize,
            "Publish": self.Publish,
            "VpcConfig": self.VpcConfig,
            "PackageType": self.PackageType,
            "DeadLetterConfig": self.DeadLetterConfig,
            "Environment": self.Environment,
            "KMSKeyArn": self.KMSKeyArn,
            "TracingConfig": self.TracingConfig,
            "Tags": self.Tags,
            "Layers": self.Layers,
            "FileSystemConfigs": self.FileSystemConfigs,
            "ImageConfig": self.ImageConfig,
            "CodeSigningConfigArn": self.CodeSigningConfigArn,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return lambdafunction_model(**filtered_data)

    def from_output(self, key: lambdafunction_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::lambda::function::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::lambda::function::{self.hash}", "key": key, "type": "cdev_output"})


class Permission(Cdev_Resource):
    """
    Revokes function-use permission from an Amazon Web Services service or another account. You can get the ID of the statement from the output of GetPolicy.


    """

    def __init__(self, cdev_name: str, FunctionName: str, StatementId: str, Action: str, Principal: str, SourceArn: str=None, SourceAccount: str=None, EventSourceToken: str=None, Qualifier: str=None, RevisionId: str=None):
        ""
        super().__init__(cdev_name)

        self.FunctionName = FunctionName
        """
        The name of the Lambda function, version, or alias.

  **Name formats** 

 *  **Function name** - `my-function` (name-only), `my-function:v1` (with alias).


*  **Function ARN** - `arn:aws:lambda:us-west-2:123456789012:function:my-function`.


*  **Partial ARN** - `123456789012:function:my-function`.



 You can append a version number or alias to any of the formats. The length constraint applies only to the full ARN. If you specify only the function name, it is limited to 64 characters in length.


        """

        self.StatementId = StatementId
        """
        A statement identifier that differentiates the statement from others in the same policy.


        """

        self.Action = Action
        """
        The action that the principal can use on the function. For example, `lambda:InvokeFunction` or `lambda:GetFunction`.


        """

        self.Principal = Principal
        """
        The Amazon Web Services service or account that invokes the function. If you specify a service, use `SourceArn` or `SourceAccount` to limit who can invoke the function through that service.


        """

        self.SourceArn = SourceArn
        """
        For Amazon Web Services services, the ARN of the Amazon Web Services resource that invokes the function. For example, an Amazon S3 bucket or Amazon SNS topic.


        """

        self.SourceAccount = SourceAccount
        """
        For Amazon S3, the ID of the account that owns the resource. Use this together with `SourceArn` to ensure that the resource is owned by the specified account. It is possible for an Amazon S3 bucket to be deleted by its owner and recreated by another account.


        """

        self.EventSourceToken = EventSourceToken
        """
        For Alexa Smart Home functions, a token that must be supplied by the invoker.


        """

        self.Qualifier = Qualifier
        """
        Specify a version or alias to add permissions to a published version of the function.


        """

        self.RevisionId = RevisionId
        """
        Only update the policy if the revision ID matches the ID that's specified. Use this option to avoid modifying a policy that has changed since you last read it.


        """

        self.hash = hasher.hash_list([self.FunctionName, self.StatementId, self.Action, self.Principal, self.SourceArn, self.SourceAccount, self.EventSourceToken, self.Qualifier, self.RevisionId])

    def render(self) -> permission_model:
        data = {
            "ruuid": "cdev::aws::lambda::permission",
            "name": self.name,
            "hash": self.hash,
            "FunctionName": self.FunctionName,
            "StatementId": self.StatementId,
            "Action": self.Action,
            "Principal": self.Principal,
            "SourceArn": self.SourceArn,
            "SourceAccount": self.SourceAccount,
            "EventSourceToken": self.EventSourceToken,
            "Qualifier": self.Qualifier,
            "RevisionId": self.RevisionId,
        }

        filtered_data = {k:v for k,v in data.items() if v}
        
        return permission_model(**filtered_data)

    def from_output(self, key: permission_output, transformer: Callable[[Any], Any]=None) -> Cloud_Output:
        if transformer:
            return Cloud_Output(**{"resource": f"cdev::aws::lambda::permission::{self.hash}", "key": key, "type": "cdev_output", "transformer": transformer})
        else:
            return Cloud_Output(**{"resource": f"cdev::aws::lambda::permission::{self.hash}", "key": key, "type": "cdev_output"})


