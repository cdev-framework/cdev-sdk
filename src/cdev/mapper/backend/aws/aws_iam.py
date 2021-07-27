import botocore
import json
import os

from cdev.models import Action_Type, Cloud_Output, Resource_State_Difference
from cdev.settings import SETTINGS

from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from cdev.resources.aws.iam import policy_model

from . import aws_client

client = aws_client.get_boto_client("iam")


def create_aws_iam_policy(identifier: str, policy: dict):
    try:
        rv = _create_aws_iam_policy(policy)
    except Exception as e:
        print(e)
        return None
    
    try:
        cdev_cloud_mapper.add_cloud_resource(identifier, policy)
        cdev_cloud_mapper.update_output_value(identifier, rv)
    except Exception as e:
        print(e)


def _create_aws_iam_policy(policy: dict):
    try:
        args = { k:v for (k,v) in policy.items() if v } 
    except Exception as e:
        print(e)
        return False


    try:
        response = client.create_policy(**args)
        print(f"AWS RESPONSE -> {response}")
    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception


    return response.get("Policy")



def handle_aws_iam_policy_deployment(resource_diff: Resource_State_Difference) -> bool:
    # TODO throw error if resource is not lambda function
    NEEDED_PARAMS = set(["PolicyName", "Path", "PolicyDocument", "Description", "Tags"])
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            policy_params = {k:v for k,v in resource_diff.new_resource.dict().items() if k in NEEDED_PARAMS}
            print(policy_params)

            create_aws_iam_policy(resource_diff.new_resource.hash, policy_params)
            print("Add POlicy")
        elif resource_diff.action_type == Action_Type.DELETE:
            print("Delete Policy")

        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            print("Update Policy")

            cdev_cloud_mapper.reidentify_cloud_resource(resource_diff.previous_resource.hash, resource_diff.new_resource.hash)
            
        
    except Exception as e:
        print(e)
        return False

    return True