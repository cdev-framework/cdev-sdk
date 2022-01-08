import time
import re
from typing import Dict
import botocore
import json

from cdev.resources.aws.s3_models import *
from cdev.models import Resource_State_Difference, Action_Type
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .aws_client import run_client_function, get_boto_client, monitor_status


################################################
##########
##########     bucket
##########
################################################


def create_bucket(identifier: str, resource: bucket_model) -> bool:
    try:
        rv = _create_bucket(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


def remove_bucket(identifier: str, resource: bucket_model) -> bool:
    try:
        _remove_bucket(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_bucket(identifier: str, resource: bucket_model) -> bucket_output:
    try:

        args = bucket_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function("s3", "create_bucket", args)

        rv = response

        print(rv)

        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_bucket(identifier: str, resource: bucket_model):
    try:

        args = bucket_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function("s3", "delete_bucket", args)

        rv = response

        print(rv)

        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_bucket_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_bucket(
                resource_diff.new_resource.hash, resource_diff.new_resource
            )
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:

            return remove_bucket(
                resource_diff.previous_resource.hash, resource_diff.previous_resource
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


################################################
##########
##########     object
##########
################################################


def create_object(identifier: str, resource: object_model) -> bool:
    try:
        rv = _create_object(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


def remove_object(identifier: str, resource: object_model) -> bool:
    try:
        _remove_object(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_object(identifier: str, resource: object_model) -> object_output:
    try:

        args = object_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function("s3", "put_object", args)

        rv = response

        print(rv)

        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_object(identifier: str, resource: object_model):
    try:

        args = object_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function("s3", "delete_object", args)

        rv = response

        print(rv)

        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_object_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_object(
                resource_diff.new_resource.hash, resource_diff.new_resource
            )
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:

            return remove_object(
                resource_diff.previous_resource.hash, resource_diff.previous_resource
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
