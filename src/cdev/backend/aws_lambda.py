import boto3
import botocore
import json

from cdev.schema import utils as schema_utils

client = boto3.client(
    "lambda",    
    aws_access_key_id="",
    aws_secret_access_key="",)

# TODO throw errors

def create_lambda_function(create_event):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.create_function

    # REQUIRED PARAMS
    # ["FunctionName", "Role", "Code"]
    try:
        schema_utils.validate(schema_utils.SCHEMA.BACKEND_LAMBDA_CREATE_FUNCTION, create_event)
    except Exception as e:
        print(e)
        return

    try:
        args = _build_configuration_arg(create_event.get("Configuration"), required=["Role", "Handler", "Runtime"])
    except Exception as e:
        print(e)
        return False

    args["Code"] = create_event.get("Code")
    args["FunctionName"] = create_event.get("FunctionName")

    try:
        response = client.create_function(**args)
        print(json.dumps(response))
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False


    return True


def update_lambda_function_code(update_code_event):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.update_function_code

    # REQUIRED PARAMS
    # ["FunctionName", "Code"]
    try:
        schema_utils.validate(schema_utils.SCHEMA.BACKEND_LAMBDA_UPDATE_FUNCTION_CODE, update_code_event)
    except Exception as e:
        print(e)
        return

    args = {}
    args["S3Bucket"] = update_code_event.get("S3Bucket")
    args["S3Key"] = update_code_event.get("S3Key")
    args["FunctionName"] = update_code_event.get("FunctionName")

    try:
        response = client.update_function_code(**args)
        print(json.dumps(response))
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False


    return True


def update_lambda_function_configuration(update_configuration_event):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.create_function

    # REQUIRED PARAMS
    # ["FunctionName"]
    try:
        schema_utils.validate(schema_utils.SCHEMA.BACKEND_LAMBDA_UPDATE_FUNCTION_CONFIGURATION, update_configuration_event)
    except Exception as e:
        print(e)
        return

    try:
        args = _build_configuration_arg(update_configuration_event.get("Configuration"))
    except Exception as e:
        print(e)
        return False


    try:
        response = client.update_function_configuration(**args)
        print(json.dumps(response))
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False

    return


def delete_lambda_function(delete_event):
    return


def _build_configuration_arg(configuration, required=[]):
    try:
        schema_utils.validate(schema_utils.SCHEMA.BACKEND_LAMBDA_CONFIGURATION, configuration)
    except Exception as e:
        print(e)
        return

    rv = {}

    for config_obj in configuration:
        rv[config_obj.get("name")] = config_obj.get("value")

    if required:
        for config_name in required:
            if not config_name in required:
                return None

    return rv
