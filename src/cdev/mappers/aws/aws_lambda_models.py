from typing import List, Union
from pydantic import BaseModel, FilePath, conint

from cdev.resources.aws import s3, lambda_function


class create_aws_lambda_function_event(BaseModel):
    """

    (AWS documentation Link)
    Model that encapsulates the needed paramaters to **CREATE** a lambda function using the boto3 client. The needed code should already
    have been uploaded to S3.

    Attributes:
        FunctionName: Name of the function
        Code: S3 object that denotes the uploaded artifact
        Configuration: Params of the AWS Lambda function
    """

    FunctionName: str
    Code: s3.s3_object
    Configuration: lambda_function.lambda_function_configuration

    def __init__(
        __pydantic_self__,
        FunctionName: str,
        Code: s3.s3_object,
        Configuration: lambda_function.lambda_function_configuration,
    ) -> None:
        super().__init__(
            **{
                "FunctionName": FunctionName,
                "Code": Code,
                "Configuration": Configuration,
            }
        )


class delete_aws_lambda_function_event(BaseModel):
    """
    (AWS documentation Link)
    Model that encapsulates the needed paramaters to **DELETE** a lambda function using the boto3 client.

    Attributes:
        FunctionName: Name of the function
    """

    FunctionName: str


class update_lambda_function_code_event(BaseModel):
    """
    (AWS documentation Link)
    Model that encapsulates the needed paramaters to **UPDATE** a lambda function's code using the boto3 client.

    Attributes:
        FunctionName: Name of the function
        Code: S3 object that denotes the uploaded artifact
    """

    FunctionName: str
    S3Bucket: str
    S3Key: str

    def __init__(
        __pydantic_self__, FunctionName: str, S3Bucket: str, S3Key: str
    ) -> None:
        super().__init__(
            **{"FunctionName": FunctionName, "S3Bucket": S3Bucket, "S3Key": S3Key}
        )


class update_lambda_configuration_event(BaseModel):
    """
    (AWS documentation Link)
    Model that encapsulates the needed paramaters to **UPDATE** a lambda function's configuration using the boto3 client.

    Attributes:
        FunctionName: Name of the function
        Configuration: Params of the AWS Lambda function
    """

    FunctionName: str
    Configuration: lambda_function.lambda_function_configuration

    def __init__(
        __pydantic_self__,
        FunctionName: str,
        Configuration: lambda_function.lambda_function_configuration,
    ) -> None:
        super().__init__(
            **{"FunctionName": FunctionName, "Configuration": Configuration}
        )


class create_lambda_eventsource_event(BaseModel):
    """
    (AWS documentation Link)
    Model that encapsulates the needed paramaters to **CREATE** a lambda function event source.

    Attributes:
        EventSourceArn: ARN of the eventsource that will trigger this lambda
        FunctionArn: ARN of the lambda function that will need to be triggered.
        Enabled: Should this eventsource be activateds
    """

    EventSourceArn: str
    FunctionArn: str
    Enabled: bool
