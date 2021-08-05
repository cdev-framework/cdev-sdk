

import time
import re
from typing import Dict
import botocore
import json

from cdev.resources.aws.dynamodb_models import *
from cdev.models import Resource_State_Difference, Action_Type
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .aws_client import run_client_function, get_boto_client, monitor_status


################################################
##########
##########     table
##########
################################################


def create_table(identifier: str, resource: table_model) -> bool:
    try:
        rv = _create_table(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

def remove_table(identifier: str, resource: table_model) -> bool:
    try:
        _remove_table(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_table(identifier: str, resource: table_model) -> table_output:
    try:

        args = table_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function('dynamodb', 'create_table', args)

        rv = response.get('TableDescription')



        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_table(identifier: str, resource: table_model):
    try:

        args = table_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function('dynamodb', 'delete_table', args)

        rv = response



        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_table_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_table(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_table(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

