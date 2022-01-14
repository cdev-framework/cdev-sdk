from typing import Dict

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.utils import logger

from core.resources.simple import api as simple_api
from core.resources.simple.xlambda import Event as lambda_event


from .. import aws_client 


log = logger.get_cdev_logger(__name__)


def _create_simple_api(identifier: str, resource: simple_api.simple_api_model) -> Dict:
    base_args = {
        "Name": resource.api_name,
        "ProtocolType": "HTTP",
    }

    cors_args = {
        "CorsConfiguration": {
            "AllowOrigins": ["*"],
            "AllowMethods": ["*"],
            "AllowHeaders": [
                "Content-Type",
                "X-Amz-Date",
                "Authorization",
                "X-Api-Key",
                "X-Amz-Security-Token",
                "X-Amz-User-Agent",
            ],
        }
    }

    _ = base_args.update(cors_args) if resource.allow_cors else None

    log.debug(base_args)
    rv = aws_client.run_client_function("apigatewayv2", "create_api", base_args)
    

    info = {
        "cloud_id": rv.get("ApiId"),
        "arn": "",
        "endpoints": {},
    }

    _stage_args = {
        "ApiId": info.get("cloud_id"),
        "AutoDeploy": True,
        "StageName": "prod",
    }
    

    rv2 = aws_client.run_client_function('apigatewayv2', 'create_route', _stage_args)

    log.debug(rv2)

    info["endpoint"] = f"{rv.get('ApiEndpoint')}/{rv2.get('StageName')}"
    api_id = info.get("cloud_id")
    if resource.routes:
        for route in resource.routes:
            route_cloud_id = _create_route(api_id, route)

            route_info = {
                "cloud_id": route_cloud_id,
                "route": route.config.get("path"),
                "verbs": route.config.get("verb"),
            }

            dict_key = f'{route.config.get("path")}:{route.config.get("verb")}'

            tmp = info.get("endpoints")
            tmp[dict_key] = route_info

            info["endpoints"] = tmp


    return True


def _remove_simple_api(identifier: str, resource: simple_api.simple_api_model) -> bool:

    api_id = cdev_cloud_mapper.get_output_value_by_hash(identifier, "cloud_id")

    aws_client.run_client_function("apigatewayv2", "delete_api", {"ApiId": api_id})

    log.debug(f"Delete information in resource and cloud state")

    return True


def _create_route(api_id, route) -> str:
    _route_args = {
        "ApiId": api_id,
        "RouteKey": f"{route.config.get('verb')} {route.config.get('path')}",
    }
    
    rv = aws_client.run_client_function('apigatewayv2', 'create_route', _route_args)
    

    return rv.get("RouteId")


def _delete_route(api_id, route_id) -> bool:

    aws_client.run_client_function(
        "apigatewayv2", "delete_route", {"ApiId": api_id, "RouteId": route_id}
    )

    return True


def _update_simple_api(
    previous_resource: simple_api.simple_api_model,
    new_resource: simple_api.simple_api_model,
):
    # Check routes
    previous_routes_hashes = set(
        [lambda_event(**x).get_hash() for x in previous_resource.routes]
    )
    new_routes_hashes = set([x.get_hash() for x in new_resource.routes])

    routes_to_be_created = []
    routes_to_be_deleted = []

    for route in new_resource.routes:
        if not route.get_hash() in previous_routes_hashes:
            routes_to_be_created.append(route)

    for route in previous_resource.routes:
        if not lambda_event(**route).get_hash() in new_routes_hashes:
            routes_to_be_deleted.append(route)

    log.debug(f"Routes to be created -> {routes_to_be_created}")
    log.debug(f"Routes to be deleted -> {routes_to_be_deleted}")

    previous_cloud_id = cdev_cloud_mapper.get_output_value_by_hash(
        previous_resource.hash, "cloud_id"
    )

    new_output_info = {}
    for route in routes_to_be_created:
        route_cloud_id = _create_route(previous_cloud_id, route)

        route_info = {
            "cloud_id": route_cloud_id,
            "route": route.config.get("path"),
            "verbs": route.config.get("verb"),
        }

        dict_key = f'{route.config.get("path")}:{route.config.get("verb")}'
        new_output_info[dict_key] = route_info

        log.debug(f"Created Route -> {route}")

    previous_route_info = cdev_cloud_mapper.get_output_value_by_hash(
        previous_resource.hash, "endpoints"
    )

    previous_route_info.update(new_output_info)

    for route in routes_to_be_deleted:
        dict_key = (
            f'{route.get("config").get("path")}:{route.get("config").get("verb")}'
        )

        _delete_route(
            previous_cloud_id, previous_route_info.get(dict_key).get("cloud_id")
        )

        previous_route_info.pop(dict_key)

        log.debug(f"Delete Route -> {dict_key}")

    return True


def handle_simple_api_deployment(transaction_token: str, namespace_token: str, resource_diff: Resource_Difference) -> bool:
    try:
        if resource_diff.action_type == Resource_Change_Type.CREATE:

            return _create_simple_api(
                resource_diff.new_resource.hash, resource_diff.new_resource
            )
        elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:

            return _update_simple_api(
                resource_diff.previous_resource, resource_diff.new_resource
            )
        elif resource_diff.action_type == Resource_Change_Type.DELETE:

            return _remove_simple_api(
                resource_diff.previous_resource.hash, resource_diff.previous_resource
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
