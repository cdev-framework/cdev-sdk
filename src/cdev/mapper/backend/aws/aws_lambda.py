import botocore
import json
import os

from cdev.models import Action_Type, Cloud_Output, Resource_State_Difference
from cdev.settings import SETTINGS

from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from cdev.resources.aws.s3 import s3_object
from cdev.resources.aws.lambda_function import aws_lambda_function

from . import aws_client
from .aws_lambda_models import *
from . import aws_s3, aws_s3_models

client = aws_client.get_boto_client("lambda")


def upload_lambda_function_code(identifier: str, lambda_resource: aws_lambda_function):
    filename = os.path.split(lambda_resource.FPath)[1]
    keyname = filename[:-3] + f"-{lambda_resource.hash}" + ".zip"

    original_zipname = filename[:-3] + ".zip"
    zip_location = os.path.join(os.path.dirname(lambda_resource.FPath), original_zipname )


    aws_s3.put_object(put_object_event=aws_s3_models.put_object_event(**{
                "Filename": zip_location,
                "Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
                "Key": keyname
    }))


    cdev_cloud_mapper.add_cloud_resource(identifier, {
            "Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
            "Key": keyname
    })


def create_lambda_function(identifier: str, lambda_resource: aws_lambda_function):
    filename = os.path.split(lambda_resource.FPath)[1]
    keyname = filename[:-3] + f"-{lambda_resource.hash}" + ".zip"
    function_name = lambda_resource.FunctionName


    base_config = { k:v for (k,v) in lambda_resource.Configuration.dict().items() if v }


    event = create_aws_lambda_function_event(function_name, s3_object(**{
                                                "S3Bucket": SETTINGS.get("S3_ARTIFACTS_BUCKET"),
                                                "S3Key": keyname
                                                }),
                                               base_config)

    _create_lambda_function(event)
    lambda_resource.Configuration = base_config

    cdev_cloud_mapper.add_cloud_resource(identifier, lambda_resource)


def update_lambda_function_code(lambda_resource: aws_lambda_function):
    filename = os.path.split(lambda_resource.FPath)[1]
    keyname = filename[:-3] + f"-{lambda_resource.hash}" + ".zip"

    _update_lambda_function_code(update_lambda_function_code_event(
        FunctionName=lambda_resource.FunctionName,
        S3Bucket=SETTINGS.get("S3_ARTIFACTS_BUCKET"),
        S3Key=keyname
    ))

def update_lambda_function_configuration(lambda_resource: aws_lambda_function):

    base_config = { k:v for (k,v) in lambda_resource.Configuration.dict().items() if v }
    _update_lambda_function_configuration(
        update_lambda_configuration_event(
            FunctionName=lambda_resource.FunctionName,
            Configuration=base_config
        )
    )


def delete_lambda_function(identifier: str, lambda_resource: aws_lambda_function):

    _delete_lambda_function(delete_aws_lambda_function_event(
        **{"FunctionName": lambda_resource.FunctionName}
    ))


    base_config = { k:v for (k,v) in lambda_resource.Configuration.items() if v }
    lambda_resource.Configuration = base_config


    cdev_cloud_mapper.remove_cloud_resource(identifier, lambda_resource)


def _create_lambda_function(create_event: create_aws_lambda_function_event) -> bool:
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
        print(f"AWS RESPONSE -> {json.dumps(response)}")
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False


    return True



def _update_lambda_function_code(update_code_event: update_lambda_function_code_event) -> bool:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.update_function_code
    
    
    REQUIRED PARAMS
    ["FunctionName", "Code"]
    """



    try:
        response = client.update_function_code(**update_code_event.dict())
        print(f"AWS RESPONSE -> {json.dumps(response)}")
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False


    return True


def _update_lambda_function_configuration(update_configuration_event: update_lambda_configuration_event) -> bool:
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
        print(f"AWS RESPONSE -> {json.dumps(response)}")
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False

    return


def _delete_lambda_function(delete_event: delete_aws_lambda_function_event):
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.delete_function

    REQUIRED PARAMS
    ["FunctionName"]
    
    """
    args ={}
    args["FunctionName"] = delete_event.FunctionName

    try:
        response = client.delete_function(**delete_event.dict())
        print(f"AWS RESPONSE -> {json.dumps(response)}")
    except botocore.exceptions.ClientError as e:
        print(e.response)
        return False

    return

def _replace_old_lambda_object(identifier: str, previous_resource: aws_lambda_function, new_resource: aws_lambda_function):
    cdev_cloud_mapper.remove_cloud_resource(identifier, previous_resource.dict())

    cdev_cloud_mapper.add_cloud_resource(identifier, new_resource)



def handle_aws_lambda_deployment(resource_diff: Resource_State_Difference) -> bool:
    # TODO throw error if resource is not lambda function
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            upload_lambda_function_code(resource_diff.new_resource.hash, resource_diff.new_resource)

            create_lambda_function(resource_diff.new_resource.hash, resource_diff.new_resource)

        elif resource_diff.action_type == Action_Type.DELETE:
            delete_lambda_function(resource_diff.previous_resource.hash, resource_diff.previous_resource)
            cdev_cloud_mapper.remove_identifier(resource_diff.previous_resource.hash)


        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            
            if not resource_diff.new_resource.src_code_hash == resource_diff.previous_resource.src_code_hash:
                # IF the source code hash is different than redeploy lambda code 
                upload_lambda_function_code(resource_diff.previous_resource.hash, resource_diff.new_resource)

                update_lambda_function_code(resource_diff.new_resource)
                print("UPDATE A LAMBDAS CODE")

            if not resource_diff.new_resource.config_hash == resource_diff.previous_resource.config_hash:
                update_lambda_function_configuration(resource_diff.new_resource)
                print("UPDATE_LAMBDA_CONFIG")

            if not resource_diff.new_resource.permission_hash == resource_diff.previous_resource.permission_hash:
                print(resource_diff.new_resource)
                print("UPDATE LAMBDA PERMISSIONS")

            _replace_old_lambda_object(resource_diff.previous_resource.hash, resource_diff.previous_resource, resource_diff.new_resource)
            cdev_cloud_mapper.reidentify_cloud_resource(resource_diff.previous_resource.hash, resource_diff.new_resource.hash)
            
        
    except Exception as e:
        print(e)
        return False

    return True


