

import time
import re
from typing import Dict
import botocore
import json

from cdev.resources.aws.apigatewayv2_models import *
from cdev.models import Resource_State_Difference, Action_Type
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .aws_client import run_client_function, get_boto_client, monitor_status


################################################
##########
##########     api
##########
################################################


def create_api(identifier: str, resource: api_model) -> bool:
    try:
        rv = _create_api(resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        return False

def remove_api(identifier: str, resource: api_model) -> bool:
    try:
        _remove_api(resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        return False


# Low level function to call actual clieant call and return response
def _create_api(resource: api_model) -> api_output:
    try:

        args = resource.filter_to_create()

        response = run_client_function('apigatewayv2', 'create_api', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


# Low level function to call actual clieant call and return response
def _remove_api(resource: api_model):
    try:

        args = resource.filter_to_remove()

        response = run_client_function('apigatewayv2', 'delete_api', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


def handle_api_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_api(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_api(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        return False

################################################
##########
##########     route
##########
################################################


def create_route(identifier: str, resource: route_model) -> bool:
    try:
        rv = _create_route(resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        return False

def remove_route(identifier: str, resource: route_model) -> bool:
    try:
        _remove_route(resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        return False


# Low level function to call actual clieant call and return response
def _create_route(resource: route_model) -> route_output:
    try:

        args = resource.filter_to_create()

        response = run_client_function('apigatewayv2', 'create_route', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


# Low level function to call actual clieant call and return response
def _remove_route(resource: route_model):
    try:

        args = resource.filter_to_remove()

        response = run_client_function('apigatewayv2', 'delete_route', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


def handle_route_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_route(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_route(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        return False

################################################
##########
##########     integration
##########
################################################


def create_integration(identifier: str, resource: integration_model) -> bool:
    try:
        rv = _create_integration(resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        return False

def remove_integration(identifier: str, resource: integration_model) -> bool:
    try:
        _remove_integration(resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        return False


# Low level function to call actual clieant call and return response
def _create_integration(resource: integration_model) -> integration_output:
    try:

        args = resource.filter_to_create()

        response = run_client_function('apigatewayv2', 'create_integration', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


# Low level function to call actual clieant call and return response
def _remove_integration(resource: integration_model):
    try:

        args = resource.filter_to_remove()

        response = run_client_function('apigatewayv2', 'delete_integration', args)

        
        print(f"AWS RESPONSE -> {response}")
        
        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


def handle_integration_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_integration(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_integration(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        return False

