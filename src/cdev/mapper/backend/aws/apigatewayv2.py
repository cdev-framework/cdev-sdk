

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
        rv = _create_api(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

def remove_api(identifier: str, resource: api_model) -> bool:
    try:
        _remove_api(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_api(identifier: str, resource: api_model) -> api_output:
    try:

        args = api_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function('apigatewayv2', 'create_api', args)

        rv = response

        #print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_api(identifier: str, resource: api_model):
    try:

        args = api_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function('apigatewayv2', 'delete_api', args)

        rv = response

        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


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
        raise Exception("COULD NOT DEPLOY")

################################################
##########
##########     route
##########
################################################


def create_route(identifier: str, resource: route_model) -> bool:
    try:
        rv = _create_route(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

def remove_route(identifier: str, resource: route_model) -> bool:
    try:
        _remove_route(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_route(identifier: str, resource: route_model) -> route_output:
    try:

        args = route_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function('apigatewayv2', 'create_route', args)

        rv = response

        ADDITIONAL_OUTPUT=['ApiId']
        for additional in ADDITIONAL_OUTPUT:
            if additional in args:
                rv[additional] = args.get(additional)
        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_route(identifier: str, resource: route_model):
    try:

        args = route_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function('apigatewayv2', 'delete_route', args)

        rv = response

        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


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
        raise Exception("COULD NOT DEPLOY")

################################################
##########
##########     integration
##########
################################################


def create_integration(identifier: str, resource: integration_model) -> bool:
    try:
        rv = _create_integration(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

def remove_integration(identifier: str, resource: integration_model) -> bool:
    try:
        _remove_integration(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_integration(identifier: str, resource: integration_model) -> integration_output:
    try:

        args = integration_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function('apigatewayv2', 'create_integration', args)

        rv = response

        ADDITIONAL_OUTPUT=['ApiId']
        for additional in ADDITIONAL_OUTPUT:
            if additional in args:
                rv[additional] = args.get(additional)
        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_integration(identifier: str, resource: integration_model):
    try:

        args = integration_model(**resource.dict()).filter_to_remove(identifier)
        print(args)
        response = run_client_function('apigatewayv2', 'delete_integration', args)

        rv = response

        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


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
        raise Exception("COULD NOT DEPLOY")

################################################
##########
##########     stage
##########
################################################


def create_stage(identifier: str, resource: stage_model) -> bool:
    try:
        rv = _create_stage(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

def remove_stage(identifier: str, resource: stage_model) -> bool:
    try:
        _remove_stage(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_stage(identifier: str, resource: stage_model) -> stage_output:
    try:

        args = stage_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function('apigatewayv2', 'create_stage', args)

        rv = response

        ADDITIONAL_OUTPUT=['ApiId']
        for additional in ADDITIONAL_OUTPUT:
            if additional in args:
                rv[additional] = args.get(additional)
        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_stage(identifier: str, resource: stage_model):
    try:

        args = stage_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function('apigatewayv2', 'delete_stage', args)

        rv = response

        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_stage_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_stage(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_stage(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

################################################
##########
##########     deployment
##########
################################################


def create_deployment(identifier: str, resource: deployment_model) -> bool:
    try:
        rv = _create_deployment(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

def remove_deployment(identifier: str, resource: deployment_model) -> bool:
    try:
        _remove_deployment(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_deployment(identifier: str, resource: deployment_model) -> deployment_output:
    try:

        args = deployment_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function('apigatewayv2', 'create_deployment', args)

        rv = response

        ADDITIONAL_OUTPUT=['ApiId']
        for additional in ADDITIONAL_OUTPUT:
            if additional in args:
                rv[additional] = args.get(additional)
        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_deployment(identifier: str, resource: deployment_model):
    try:

        args = deployment_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function('apigatewayv2', 'delete_deployment', args)

        rv = response

        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_deployment_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_deployment(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_deployment(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

