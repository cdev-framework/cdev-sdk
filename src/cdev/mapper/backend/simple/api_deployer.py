from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import api as simple_api
from cdev.resources.simple.xlambda import Event as lambda_event
from cdev.resources.aws import apigatewayv2_models
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from ..aws import apigatewayv2 as apigatewayv2_deployer
from ..aws import aws_client as raw_aws_client


log = logger.get_cdev_logger(__name__)


def _create_simple_api(identifier: str, resource: simple_api.simple_api_model) -> bool:

    # First create the API Gateway V2 resource

    #_api_model = apigatewayv2_models.api_model(
    #    **{
    #        "ruuid": "",
    #        "hash": "",
    #        "name": "",
    #        "Name": resource.api_name,
    #        "ProtocolType": apigatewayv2_models.ProtocolType.HTTP,
    #    }
    #)
#
    #rv = apigatewayv2_deployer._create_api("", _api_model)

    base_args =  {
        "Name": resource.api_name,
        "ProtocolType": 'HTTP',
    }

    cors_args = {
        "CorsConfiguration": {
            "AllowOrigins": [
                "*"
            ],
            "AllowMethods": [
                "*"
            ],
            "AllowHeaders": [
                "Content-Type",
                "X-Amz-Date",
                "Authorization",
                "X-Api-Key",
                "X-Amz-Security-Token",
                "X-Amz-User-Agent"
            ]
        }
    }

    _ = base_args.update(cors_args) if resource.allow_cors else None

    
    log.debug(base_args)
    rv = raw_aws_client.run_client_function("apigatewayv2", "create_api", base_args)


    info = {
        "ruuid": resource.ruuid,
        "cdev_name": resource.name,
        "cloud_id": rv.get("ApiId"),
        "arn": "",
        "endpoints": {}
    }

    _stage_model = apigatewayv2_models.stage_model(**{
        "ruuid": "",
        "hash": "",
        "name": "",
        "ApiId": info.get('cloud_id'),
        "AutoDeploy": True,
        "StageName": "prod"
    })

    rv2 = apigatewayv2_deployer._create_stage("", _stage_model)

    log.debug(rv2)

    info['endpoint'] = f"{rv.get('ApiEndpoint')}/{rv2.get('StageName')}"
    api_id = info.get('cloud_id')
    if resource.routes:
        for route in resource.routes:
            route_cloud_id = _create_route(api_id, route)
            

            route_info = {
                "cloud_id": route_cloud_id,
                "route": route.config.get("path"),
                "verbs": route.config.get("verb")
            }

            dict_key = f'{route.config.get("path")}:{route.config.get("verb")}'

            tmp =  info.get('endpoints')
            tmp[dict_key] = route_info

            info['endpoints'] = tmp



    cdev_cloud_mapper.add_identifier(identifier)
    cdev_cloud_mapper.update_output_value(identifier, info)

    return True



def _remove_simple_api(identifier: str, resource: simple_api.simple_api_model) -> bool:
    
    api_id = cdev_cloud_mapper.get_output_value(identifier, "cloud_id")

    raw_aws_client.run_client_function("apigatewayv2", "delete_api", {
        "ApiId": api_id
    })
    
    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")
    
    return True


def _create_route(api_id, route) -> str:
    _route_model = apigatewayv2_models.route_model(
                **{
                    "ruuid": "",
                    "hash": "",
                    "name": "",
                    "ApiId": api_id,
                    "RouteKey": f"{route.config.get('verb')} {route.config.get('path')}"
                }
            )

    rv = apigatewayv2_deployer._create_route("", _route_model)



    return rv.get("RouteId")


def _delete_route(api_id, route_id) -> bool:
    
    raw_aws_client.run_client_function("apigatewayv2", "delete_route", {
        "ApiId": api_id,
        "RouteId": route_id
    })

    return True

def _update_simple_api(previous_resource: simple_api.simple_api_model, new_resource: simple_api.simple_api_model):
    #Check routes
    previous_routes_hashes = set([lambda_event(**x).get_hash() for x in previous_resource.routes])
    new_routes_hashes = set([x.get_hash() for x in new_resource.routes])

    routes_to_be_created = []
    routes_to_be_deleted = []
    
    for route in new_resource.routes:
        if not route.get_hash() in previous_routes_hashes:
            routes_to_be_created.append(route)

    for route in previous_resource.routes:
        if not lambda_event(**route).get_hash() in new_routes_hashes:
            routes_to_be_deleted.append(route)

    log.debug(f'Routes to be created -> {routes_to_be_created}')
    log.debug(f'Routes to be deleted -> {routes_to_be_deleted}')

    previous_cloud_id = cdev_cloud_mapper.get_output_value(previous_resource.hash, "cloud_id")

    new_output_info = {}
    for route in routes_to_be_created:
        route_cloud_id = _create_route(previous_cloud_id, route)

        route_info = {
            "cloud_id": route_cloud_id,
            "route": route.config.get("path"),
            "verbs": route.config.get("verb")
        }

        dict_key = f'{route.config.get("path")}:{route.config.get("verb")}'
        new_output_info[dict_key] = route_info

        log.debug(f"Created Route -> {route}")

    previous_route_info = cdev_cloud_mapper.get_output_value(previous_resource.hash, "endpoints")

    previous_route_info.update(new_output_info)


    
    for route in routes_to_be_deleted:
        dict_key = f'{route.get("config").get("path")}:{route.get("config").get("verb")}'

        _delete_route(previous_cloud_id, previous_route_info.get(dict_key).get("cloud_id"))
        
        previous_route_info.pop(dict_key)

        log.debug(f"Delete Route -> {dict_key}")
        
        
    cdev_cloud_mapper.reidentify_cloud_resource(previous_resource.hash, new_resource.hash)
    cdev_cloud_mapper.update_output_by_key(new_resource.hash, "endpoints", previous_route_info)
    return True


def handle_simple_api_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return _create_simple_api(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return _update_simple_api(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return _remove_simple_api(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
