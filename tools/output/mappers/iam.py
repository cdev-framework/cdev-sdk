

import time
import re
from typing import Dict
import botocore
import json

from cdev.resources.aws.iam_models import *
from cdev.models import Resource_State_Difference, Action_Type
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .aws_client import run_client_function, get_boto_client, monitor_status


################################################
##########
##########     policy
##########
################################################


def create_policy(identifier: str, resource: policy_model) -> bool:
    try:
        rv = _create_policy(resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        return False

def remove_policy(identifier: str, resource: policy_model) -> bool:
    try:
        _remove_policy(resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        return False


# Low level function to call actual clieant call and return response
def _create_policy(resource: policy_model) -> policy_output:
    try:

        args = resource.filter_to_create()

        response = run_client_function('iam', 'create_policy', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


# Low level function to call actual clieant call and return response
def _remove_policy(resource: policy_model):
    try:

        args = resource.filter_to_remove()

        response = run_client_function('iam', 'delete_policy', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


def handle_policy_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_policy(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_policy(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        return False

################################################
##########
##########     role
##########
################################################


def create_role(identifier: str, resource: role_model) -> bool:
    try:
        rv = _create_role(resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        return False

def remove_role(identifier: str, resource: role_model) -> bool:
    try:
        _remove_role(resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        return False


# Low level function to call actual clieant call and return response
def _create_role(resource: role_model) -> role_output:
    try:

        args = resource.filter_to_create()

        response = run_client_function('iam', 'create_role', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


# Low level function to call actual clieant call and return response
def _remove_role(resource: role_model):
    try:

        args = resource.filter_to_remove()

        response = run_client_function('iam', 'delete_role', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


def handle_role_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_role(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_role(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        return False

