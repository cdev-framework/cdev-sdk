from typing import Any, Dict, FrozenSet
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.output.output_manager import OutputTask
from core.resources.simple import api as simple_api

from .. import aws_client 



def _create_simple_api(
        transaction_token: str, 
        namespace_token: str, 
        resource: simple_api.simple_api_model, 
        output_task: OutputTask
    ) -> Dict:
    """
    Create an API on AWS.

    Args:
        transaction_token (str): Transaction token to use to identify this action over a resource.
        namespace_token (str): Token used to make sure that resources are created properly in AWS.
        resource (simple_api.simple_api_model): The information about what should be deployed.
        output_task (OutputTask): Output Task to send any progress information.

    Raises:
        e: [description]

    Returns:
        Dict: Information from the cloud about the resource.
    """
    
    base_args = {
        "Name": f"cdev-api-{namespace_token}-{str(uuid4())}",
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

    if resource.allow_cors:
        base_args.update(cors_args)

    output_task.update(advance=1, comment='Creating Api')

    try:
        rv = aws_client.run_client_function("apigatewayv2", "create_api", base_args)
    except Exception as e:
        output_task.print_error(e)
        raise e 


    info = {
        "cloud_id": rv.get("ApiId"),
        "endpoints": {},
    }

    _stage_args = {
        "ApiId": info.get("cloud_id"),
        "AutoDeploy": True,
        "StageName": "prod",
    }
    
    output_task.update(advance=1, comment='Creating Stage')
    try:
        rv2 = aws_client.run_client_function('apigatewayv2', 'create_stage', _stage_args)
    except Exception as e:
        output_task.print_error(e)
        raise e 

    info["endpoint"] = f"{rv.get('ApiEndpoint')}/{rv2.get('StageName')}"
    api_id = info.get("cloud_id")
    if resource.routes:
        for route in resource.routes:
            output_task.update(advance=1, comment=f'Creating Route {route.path} [{route.verb}]')
            
            try:
                route_cloud_id = _create_route(api_id, route)
            except Exception as e:
                output_task.print_error(e)
                raise e 

            route_info = {
                "cloud_id": route_cloud_id,
                "route": route.path,
                "verbs": route.verb,
            }

            dict_key = f'{route.path}:{route.verb}'

            tmp = info.get("endpoints")
            tmp[dict_key] = route_info

            info["endpoints"] = tmp


    return info


def _update_simple_api(
    transaction_token: str, 
    namespace_token: str,
    previous_resource: simple_api.simple_api_model,
    new_resource: simple_api.simple_api_model,
    previous_output: Dict,
    output_task: OutputTask
    ) -> Dict:
    """
    Create an API on AWS.

    Args:
        transaction_token (str): Transaction token to use to identify this action over a resource.
        namespace_token (str): Token used to make sure that resources are created properly in AWS.
        previous_resource (simple_api.simple_api_model): The information about the previous API.
        new_resource (simple_api.simple_api_model): The information about the new API.
        previous_output (Dict): Cloud output of the previous resource.
        output_task (OutputTask): Output Task to send any progress information.

    Raises:
        e: [description]

    Returns:
        Dict: Information from the cloud about the resource.
    """

    previous_cloud_id = previous_output.get('cloud_id')

    output_task.print(previous_resource)

    
    # Change the CORS Settings of the API
    if not previous_resource.allow_cors == new_resource.allow_cors:
        new_cors_policy =  {
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
        } if new_resource.allow_cors else {}

        output_task.update(advance=1, comment=f'Updating CORS Policy')
        try:
            aws_client.run_client_function(
                'apigatewayv2', 
                'update_api', 
                {
                    'api_id': previous_cloud_id,
                    'CorsConfiguration ': new_cors_policy
                }
            )
        except Exception as e:
            output_task.print_error(e)
            raise e 

    
    
   
    # Delete any route that is not in the new routes but in previous routes
    routes_to_be_deleted: FrozenSet[simple_api.route_event_model] = previous_resource.routes.difference(new_resource.routes)
    # Create any route that is in the new routes but not in previous routes
    routes_to_be_created: FrozenSet[simple_api.route_event_model] = new_resource.routes.difference(previous_resource.routes)

    new_output_info = {}
    for route in routes_to_be_created:

        output_task.update(advance=1, comment=f'Creating Route {route.path} [{route.verb}]')
        try:
            route_cloud_id = _create_route(previous_cloud_id, route)
        except Exception as e:
            output_task.print_error(e)
            raise e 

        route_info = {
            "cloud_id": route_cloud_id,
            "route": route.path,
            "verbs": route.verb,
        }

        dict_key = f'{route.path}:{route.verb}'
        new_output_info[dict_key] = route_info


    
    previous_route_info: Dict[str,str] = previous_output.get('endpoints')
    
    for route in routes_to_be_deleted:
        dict_key = (
            f'{route.path}:{route.verb}'
        )

        output_task.update(advance=1, comment=f'Deleting Route {route.path} [{route.verb}]')
        try:
            _delete_route(
                previous_cloud_id, previous_route_info.get(dict_key).get("cloud_id")
            )
        except Exception as e:
            output_task.print_error(e)
            raise e 

        previous_route_info.pop(dict_key)


    previous_route_info.update(new_output_info)
    previous_output['endpoints'] = previous_route_info

    return previous_output


def _remove_simple_api(
    transaction_token: str,  
    previous_output: Dict, 
    output_task: OutputTask
    ):
    """
    Delete an API from AWS.

    Args:
        transaction_token (str): Transaction token to use to identify this action over a resource.
        previous_output (Dict): Cloud output of the resource. Used to determine what API to delete on AWS.
        output_task (OutputTask): Output Task to send any progress information.

    Raises:
        e: [description]
    """

    api_id = previous_output.get("cloud_id")

    output_task.update(advance=1, comment=f'Deleting API')

    try:
        aws_client.run_client_function("apigatewayv2", "delete_api", {"ApiId": api_id})
    except Exception as e:
        output_task.print_error(e)
        raise e 

    



def _create_route(api_id: str, route: simple_api.route_event_model) -> str:
    """
    Helper Function for creating routes on an API. Note that any error raised by the aws client will not be caught by this function and should
    be handled by the caller of this function.

    Args:
        api_id (str): Api ID of the api in AWS.
        route (simple_api.route_event_model): Information about the route to create.

    Returns:
        str: Route ID of the create route.
    """
    _route_args = {
        "ApiId": api_id,
        "RouteKey": f"{route.verb} {route.path}",
    }
    

    rv = aws_client.run_client_function('apigatewayv2', 'create_route', _route_args)
    

    return rv.get("RouteId")


def _delete_route(api_id: str, route_id: str):
    """
    Helper Function for deleting routes on an API. Note that any error raised by the aws client will not be caught by this function and should
    be handled by the caller of this function.

    Args:
        api_id (str): Api ID of the api in AWS.
        route_id (lambda_event): Route ID of the route in AWS.
    """

    aws_client.run_client_function(
        "apigatewayv2", "delete_route", {"ApiId": api_id, "RouteId": route_id}
    )




def handle_simple_api_deployment(
        transaction_token: str, 
        namespace_token: str, 
        resource_diff: Resource_Difference, 
        previous_output: Dict[str, Any],
        output_task: OutputTask
        ) -> Dict:
    
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        return _create_simple_api(
            transaction_token,
            namespace_token,
            resource_diff.new_resource,
            output_task
        )
    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:

        return _update_simple_api(
            transaction_token,
            namespace_token,
            simple_api.simple_api_model(**resource_diff.previous_resource.dict()),
            resource_diff.new_resource,
            previous_output,
            output_task
        )
        
    elif resource_diff.action_type == Resource_Change_Type.DELETE:

        _remove_simple_api(
            transaction_token,
            previous_output,
            output_task
        )

        return {}

