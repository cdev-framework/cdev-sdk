

import time
import re
from typing import Dict
import botocore
import json

from cdev.resources.aws.apigateway_models import *
from cdev.models import Resource_State_Difference, Action_Type
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .aws_client import run_client_function, get_boto_client, monitor_status


################################################
##########
##########     restapi
##########
################################################


def create_restapi(identifier: str, resource: restapi_model) -> bool:
    try:
        rv = _create_restapi(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

def remove_restapi(identifier: str, resource: restapi_model) -> bool:
    try:
        _remove_restapi(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_restapi(identifier: str, resource: restapi_model) -> restapi_output:
    try:

        args = restapi_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function('apigateway', 'create_rest_api', args)

        rv = response


        extra_info_needs = [{'final_name': 'root_resource_id', 'key': 'items', 'transform': lambda x: x[0].get('id')}]
        extra_info_call_args_keys = {'id': 'restApiId' }
        extra_info_call_args = {extra_info_call_args_keys.get(k):v for k,v in rv.items() if k in extra_info_call_args_keys}

        extra_info = run_client_function('apigateway', "get_resources", extra_info_call_args)

        for extra_info_need in extra_info_needs:
            if 'transform' in extra_info_need:
                rv[extra_info_need.get('final_name')] = extra_info_need.get('transform')(extra_info.get(extra_info_need.get('key')))
            else:
                rv[extra_info_need.get('final_name')] = extra_info.get(extra_info_need.get('key'))

        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_restapi(identifier: str, resource: restapi_model):
    try:

        args = restapi_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function('apigateway', 'delete_rest_api', args)

        rv = response



        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_restapi_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_restapi(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_restapi(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

################################################
##########
##########     resource
##########
################################################


def create_resource(identifier: str, resource: resource_model) -> bool:
    try:
        rv = _create_resource(identifier, resource)
        if rv:
            cdev_cloud_mapper.add_cloud_resource(identifier, resource)
            cdev_cloud_mapper.update_output_value(identifier, rv)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")

def remove_resource(identifier: str, resource: resource_model) -> bool:
    try:
        _remove_resource(identifier, resource)

        cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
        cdev_cloud_mapper.remove_identifier(identifier)

        return True

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _create_resource(identifier: str, resource: resource_model) -> resource_output:
    try:

        args = resource_model(**resource.dict()).filter_to_create(identifier)

        response = run_client_function('apigateway', 'create_resource', args)

        rv = response

        ADDITIONAL_OUTPUT=['restApiId']
        for additional in ADDITIONAL_OUTPUT:
            if additional in args:
                rv[additional] = args.get(additional)


        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


# Low level function to call actual clieant call and return response
def _remove_resource(identifier: str, resource: resource_model):
    try:

        args = resource_model(**resource.dict()).filter_to_remove(identifier)

        response = run_client_function('apigateway', 'delete_resource', args)

        rv = response



        print(rv)


        return rv

    except botocore.exceptions.ClientError as e:
        print(e.response)
        raise Exception("COULD NOT DEPLOY")


def handle_resource_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_resource(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_resource(resource_diff.previous_resource.hash, resource_diff.previous_resource)

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

        response = run_client_function('apigateway', 'put_integration', args)

        rv = response

        ADDITIONAL_OUTPUT=['restApiId', 'resourceId']
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

        response = run_client_function('apigateway', 'delete_integration', args)

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

        response = run_client_function('apigateway', 'create_stage', args)

        rv = response

        ADDITIONAL_OUTPUT=['restApiId']
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

        response = run_client_function('apigateway', 'delete_stage', args)

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

        response = run_client_function('apigateway', 'create_deployment', args)

        rv = response

        ADDITIONAL_OUTPUT=['restApiId', 'deploymentId']
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

        response = run_client_function('apigateway', 'delete_deployment', args)

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
