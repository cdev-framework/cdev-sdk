from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import xlambda as simple_lambda
from cdev.resources.aws import s3_models, lambda_models
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from ..aws import s3 as s3_deployer
from ..aws import xlambda as lambda_deployer

from ..aws import aws_client

from cdev.settings import SETTINGS
import os


log = logger.get_cdev_logger(__name__)

BUCKET = SETTINGS.get("S3_ARTIFACTS_BUCKET")


def create_simple_lambda(identifier: str, resource: simple_lambda.simple_aws_lambda_function_model) -> bool:
    log.info(resource)

    keyname = resource.name + f"-{resource.hash}" + ".zip"

    original_zipname = resource.configuration.Handler.split(".")[0] + ".zip"
    zip_location = os.path.join(os.path.dirname(os.path.abspath(resource.filepath)), original_zipname )
    
    log.info(f"KEYNAME {keyname}; ZIPLOCATION {zip_location}; is valid file {os.path.isfile(zip_location)}")

    # CREATE S3 artifact
    with open(zip_location, "rb") as fh:
        object_model = s3_models.object_model(**{
            "ruuid": "",
            "hash": "",
            "name": "",
            "Bucket": BUCKET,
            "Key": keyname,
            "Body": fh.read()
        })
        rv = s3_deployer._create_object("", object_model)
    log.info(rv)

    lambda_model = lambda_models.lambdafunction_model(**{
        "ruuid": "",
        "hash": "",
        "name": "",
        "FunctionName": resource.name,
        "Runtime": lambda_models.Runtime.python3_7,
        "Role": "arn:aws:iam::369004794337:role/test-lambda-role",
        "Handler": resource.configuration.Handler,
        "Code": lambda_models.FunctionCode(S3Bucket=BUCKET, S3Key=keyname),
        "Environment": resource.configuration.Environment
    })

    lambda_deployer._create_lambdafunction("", lambda_model)

    aws_client.run_client_function("lambda", "add_permission", {
        "FunctionName": resource.name,
        "Action": "lambda:InvokeFunction",
        "Principal": "apigateway.amazonaws.com",
        "StatementId": f"stmt-{resource.name}",
    })


    return True


def remove_simple_lambda(identifier: str, resource: simple_lambda.simple_aws_lambda_function_model) -> bool:
    return True


def handle_simple_lambda_function_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_simple_lambda(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_simple_lambda(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
