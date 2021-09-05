from typing import Dict
from cdev.resources.aws.apigatewayv2_models import integration_model, IntegrationType
from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import xlambda as simple_lambda
from cdev.resources.aws import s3_models, lambda_models
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from ..aws import s3 as s3_deployer
from ..aws import xlambda as lambda_deployer
from ..aws import apigatewayv2 as apigateway_deployer
from ..aws import aws_client as raw_aws_client

from ..aws import aws_client

from .lambda_event_deployer import EVENT_TO_HANDLERS

from cdev.settings import SETTINGS
import os


log = logger.get_cdev_logger(__name__)

BUCKET = SETTINGS.get("S3_ARTIFACTS_BUCKET")


def _create_simple_lambda(identifier: str, resource: simple_lambda.simple_aws_lambda_function_model) -> bool:
    # Steps for creating a deployed lambda function
    # 1. Upload the artifact to S3 as the archive location
    # 2. Create the function
    # 3. Create any integrations that are need based on Events passed in
    
    
    log.debug(f"Attempting to create {resource}")

    # Step 1
    keyname = _upload_s3_code_artifact(resource)
   
    final_info = {
        "ruuid": resource.ruuid,
        "cdev_name": resource.name,
    }


    final_info['artifact_bucket'] = BUCKET
    final_info['artifact_key'] = keyname

    # Step 2

    lambda_function_args = {
        "FunctionName": resource.name,
        "Runtime": lambda_models.Runtime.python3_7,
        "Role": "arn:aws:iam::369004794337:role/test-lambda-role",
        "Handler": resource.configuration.Handler,
        "Code": {"S3Bucket":BUCKET, "S3Key":keyname},
        "Environment": resource.configuration.Environment.dict() if resource.configuration.Environment else {}
    }

    lambda_function_rv = raw_aws_client.run_client_function("lambda", "create_function", lambda_function_args)

    final_info['cloud_id'] = lambda_function_rv.get("FunctionArn")

    # Step 3
    log.debug(f"lambda events -> {resource.events}")
    if resource.events:
        event_hash_to_output = {}
        for event in resource.events:
            log.debug(f"Adding event -> {event}")

            key =  event.event_type
            log.debug(key)
            if not key in EVENT_TO_HANDLERS:
                raise Exception

            output = EVENT_TO_HANDLERS.get(key).get("CREATE")(event, final_info.get("cloud_id"))
            event_hash_to_output[event.get_hash()] = output

        final_info['events'] = event_hash_to_output


    cdev_cloud_mapper.add_identifier(identifier)
    cdev_cloud_mapper.update_output_value(identifier, final_info)

    return True


def _upload_s3_code_artifact(resource: simple_lambda.simple_aws_lambda_function_model) -> str:
    # Takes in a resource and create an s3 artifact that can be use as src code for lambda deployment
    keyname = resource.name + f"-{resource.hash}" + ".zip"
    original_zipname = resource.configuration.Handler.split(".")[0] + ".zip"
    zip_location = os.path.join(os.path.dirname(os.path.abspath(resource.filepath)), original_zipname )
    
    log.debug(f"artifact keyname {keyname}; ondisk location {zip_location}; is valid file {os.path.isfile(zip_location)}")

    if not os.path.isfile(zip_location):
        #TODO better exception
        log.error(f"bad archive local path given {zip_location}")
        raise Exception



    log.debug(f"upload artifact to s3")
    with open(zip_location, "rb") as fh:
        object_args = {
            "Bucket": BUCKET,
            "Key": keyname,
            "Body": fh.read()
        }
        raw_aws_client.run_client_function("s3", "put_object", object_args)

    return keyname


def _remove_simple_lambda(identifier: str, resource: simple_lambda.simple_aws_lambda_function_model) -> bool:
    # Steps:
    # Remove and event that is on the function to make sure resources are properly cleaned up
    # Remove the actual function
    log.debug(f"Attempting to delete {resource}")
    cloud_id = cdev_cloud_mapper.get_output_value(resource.hash, "cloud_id")
    log.debug(f"Current function ARN {cloud_id}")

    for event in resource.events:
        casted_event = simple_lambda.Event(**event)

        key =  casted_event.event_type

        if not key in EVENT_TO_HANDLERS:
            raise Exception

        output = EVENT_TO_HANDLERS.get(key).get("REMOVE")(casted_event, resource.hash)


    raw_aws_client.run_client_function("lambda", "delete_function", {"FunctionName": cloud_id})
    log.debug(f"Delete function")

    
    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")
    
    return True


def _update_simple_lambda(previous_resource: simple_lambda.simple_aws_lambda_function_model,  new_resource: simple_lambda.simple_aws_lambda_function_model) -> bool:
    # Updates can be of:
    # Update source code or dependencies
    # Update configuration
    # Update events
    
    
    updated_info = {

    }
    log.debug(previous_resource)
    if not previous_resource.config_hash == new_resource.config_hash:
        if not previous_resource.configuration.get("Environment") == new_resource.configuration.Environment:
            log.debug(f"UPDATE ENVIRONMENT VARIABLES: {previous_resource.configuration.get('Environment')} -> {new_resource.configuration.Environment}")
            raw_aws_client.run_client_function("lambda", "update_function_configuration", {
                "FunctionName": cdev_cloud_mapper.get_output_value(previous_resource.hash, "cloud_id"),
                "Environment": new_resource.configuration.Environment.dict()
            })
        

    if not previous_resource.src_code_hash == new_resource.src_code_hash:
        log.debug(f"UPDATE SOURCE CODE OF {previous_resource.name}; {previous_resource.src_code_hash} -> {new_resource.src_code_hash}")
        
        keyname = _upload_s3_code_artifact(new_resource)
        updated_info['artifact_key'] = keyname

        raw_aws_client.run_client_function("lambda", "update_function_code", {
            "FunctionName": cdev_cloud_mapper.get_output_value(previous_resource.hash, "cloud_id"),
            "S3Key": keyname,
            "S3Bucket": BUCKET,
            "Publish": True
        })


    if not previous_resource.events_hash == new_resource.events_hash:
        log.debug(f"UPDATE HASH: {previous_resource.events} -> {new_resource.events}")

        previous_hashes = set([simple_lambda.Event(**x).get_hash() for x in previous_resource.events])
        new_hashes = set([x.get_hash() for x in new_resource.events])

        create_events = []
        remove_events = []

        event_output = cdev_cloud_mapper.get_output_value(previous_resource.hash, "events")
        if not event_output:
            event_output = {}

            
        for event in new_resource.events:
            if not event.get_hash() in previous_hashes:
                create_events.append(event)

            
        for event in previous_resource.events:
            if not simple_lambda.Event(**event).get_hash() in new_hashes:
                remove_events.append(event)

        log.debug(f"New Events -> {create_events}")
        log.debug(f"Previous Events -> {remove_events}")

        for event in create_events:
            key =  event.event_type
            log.debug(key)
            if not key in EVENT_TO_HANDLERS:
                raise Exception

            output = EVENT_TO_HANDLERS.get(key).get("CREATE")(event, cdev_cloud_mapper.get_output_value(previous_resource.hash, "cloud_id"))
            event_output[event.get_hash()] = output
            log.debug(f"Add Event -> {event}")

        
        for event in remove_events:
            casted_event = simple_lambda.Event(**event)

            key =  casted_event.event_type

            if not key in EVENT_TO_HANDLERS:
                raise Exception

            output = EVENT_TO_HANDLERS.get(key).get("REMOVE")(casted_event, previous_resource.hash)
            event_output.pop(casted_event.get_hash())
            log.debug(f"Remove Event -> {casted_event}")

        cdev_cloud_mapper.update_output_by_key(previous_resource.hash, "events", event_output)


    cdev_cloud_mapper.reidentify_cloud_resource(previous_resource.hash, new_resource.hash)

    return True


def handle_simple_lambda_function_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_lambda(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return _update_simple_lambda(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return _remove_simple_lambda(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")



