import time
import re
from typing import Dict
import botocore
import json

from cdev.resources.aws.lambda_models import *
from cdev.models import Resource_State_Difference, Action_Type
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .aws_client import run_client_function, get_boto_client, monitor_status


################################################
##########
##########     lambdafunction
##########
################################################


def create_lambdafunction(identifier: str, resource: lambdafunction_model) -> bool:
    try:
        rv = _create_lambdafunction(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


def remove_lambdafunction(identifier: str, resource: lambdafunction_model) -> bool:
    try:
        _remove_lambdafunction(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_lambdafunction(
    identifier: str, resource: lambdafunction_model
) -> lambdafunction_output:
    try:

        args = lambdafunction_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function("lambda", "create_function", args)

        rv = response

        # print(rv)

        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_lambdafunction(identifier: str, resource: lambdafunction_model):
    try:

        args = lambdafunction_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function("lambda", "delete_function", args)

        rv = response

        # print(rv)

        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_lambdafunction_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_lambdafunction(
                resource_diff.new_resource.hash, resource_diff.new_resource
            )
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:

            return remove_lambdafunction(
                resource_diff.previous_resource.hash, resource_diff.previous_resource
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


################################################
##########
##########     permission
##########
################################################


def create_permission(identifier: str, resource: permission_model) -> bool:
    try:
        rv = _create_permission(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


def remove_permission(identifier: str, resource: permission_model) -> bool:
    try:
        _remove_permission(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_permission(
    identifier: str, resource: permission_model
) -> permission_output:
    try:

        args = permission_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function("lambda", "add_permission", args)

        rv = response

        print(rv)

        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_permission(identifier: str, resource: permission_model):
    try:

        args = permission_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function("lambda", "remove_permission", args)

        rv = response

        print(rv)

        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_permission_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_permission(
                resource_diff.new_resource.hash, resource_diff.new_resource
            )
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:

            return remove_permission(
                resource_diff.previous_resource.hash, resource_diff.previous_resource
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
