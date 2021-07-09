import botocore
import json

from . import aws_client
from .aws_lambda_models import *

client = aws_client.get_boto_client("lambda")

# TODO throw errors

def create_lambda_function(create_event: create_aws_lambda_function) -> bool:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.create_functio
    
    REQUIRED PARAMS
    ["FunctionName", "Role", "Code"]
    """
    try:
        args = create_event.Configuration.dict()
    except Exception as e:
        print(e)
        return False

    args["Code"] = create_event.Code.dict()
    args["FunctionName"] = create_event.FunctionName

    try:
        response = client.create_function(**args)
        print(json.dumps(response))
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False


    return True


def update_lambda_function_code(update_code_event: update_lambda_function_code) -> bool:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.update_function_code
    
    
    REQUIRED PARAMS
    ["FunctionName", "Code"]
    """

    args = {}
    args["S3Bucket"] = update_code_event.Code.S3Bucket
    args["S3Key"] = update_code_event.Code.S3Key
    args["FunctionName"] = update_code_event.FunctionName

    try:
        response = client.update_function_code(**args)
        print(json.dumps(response))
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False


    return True


def update_lambda_function_configuration(update_configuration_event: update_lambda_configuration) -> bool:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.update_function_configuratio
    
    REQUIRED PARAMS
    ["FunctionName"]
    """
    try:
        args = update_configuration_event.Configuration.dict()
    except Exception as e:
        print(e)
        return False
    args["FunctionName"] = update_configuration_event.FunctionName


    try:
        response = client.update_function_configuration(**args)
        print(json.dumps(response))
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False

    return


def delete_lambda_function(delete_event: delete_aws_lambda_function):
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.delete_function

    REQUIRED PARAMS
    ["FunctionName"]
    
    """
    args ={}
    args["FunctionName"] = delete_event.FunctionName

    try:
        response = client.delete_function(**args)
        print(json.dumps(response))
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False

    return


