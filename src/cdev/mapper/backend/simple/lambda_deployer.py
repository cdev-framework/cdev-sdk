from cdev.resources.aws.apigatewayv2_models import integration_model, IntegrationType
from threading import Event
from typing_extensions import final
from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import xlambda as simple_lambda
from cdev.resources.aws import s3_models, lambda_models
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from ..aws import s3 as s3_deployer
from ..aws import xlambda as lambda_deployer
from ..aws import apigatewayv2 as apigateway_deployer

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

    final_info = {}

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

    final_info['artifact_bucket'] = BUCKET
    final_info['artifact_key'] = keyname

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

    rv = lambda_deployer._create_lambdafunction("", lambda_model)

    final_info['cloud_id'] = rv.get("FunctionArn")

    log.debug(resource.events)
    if resource.events:
        for event in resource.events:
            log.info(f"Adding event -> {event}")
            handle_adding_api_event(event, final_info.get("cloud_id"))



    permission_model = lambda_models.permission_model(**{
        "ruuid": "",
        "hash": "",
        "name": "",
        "FunctionName": resource.name,
        "Action": "lambda:InvokeFunction",
        "Principal": "apigateway.amazonaws.com",
        "StatementId": f"stmt-{resource.name}",
    })

    rv = lambda_deployer._create_permission("", permission_model)
    log.info(rv)


    cdev_cloud_mapper.add_cloud_resource(identifier, resource)
    cdev_cloud_mapper.update_output_value(identifier, final_info)

    return True


def handle_adding_api_event(event, cloud_function_id):
    api_resource = cdev_cloud_mapper.get_output_value_by_name("cdev::simple::api", event.original_resource_id)
    log.info(f"FOUND RESOURCE -> {api_resource}")
    api_id = api_resource.get("cloud_id")
    routes = api_resource.get("endpoints")

    route_id=""
    for route in routes:
        if routes.get(route).get("route") == event.config.get("path") and routes.get(route).get("verbs") == event.config.get("verb"):
            log.info(f"FOUND CORRECT ROUTE -> {route}")
            route_id = routes.get(route).get("cloud_id")
            break

    log.info(f"Route ID -> {route_id}")

    created_integration_model = integration_model(**{
        "ruuid": "",
        "hash": "",
        "name": "",
        "ApiId": api_id,
        "IntegrationType": IntegrationType.AWS_PROXY,
        "IntegrationUri": cloud_function_id,
        "PayloadFormatVersion": "2.0"

    })
    rv = apigateway_deployer._create_integration("", created_integration_model)

    log.info(rv)




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
