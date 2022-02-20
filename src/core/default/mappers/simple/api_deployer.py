from typing import Any, Dict, FrozenSet
from uuid import uuid4
from core.constructs.models import frozendict

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.constructs.output_manager import OutputTask
from core.default.resources.simple import api as simple_api

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

    api_id = rv.get("ApiId")

    info = {
        "cloud_id": api_id,
        "endpoints": {},
    }

    
    if resource.authorizers:
        _authorizer_outputs: Dict[str, simple_api.authorizer_model] = {}
        
        for authorizer in resource.authorizers:
            output_task.update(advance=1, comment=f'Creating Authorizer {authorizer.name}')
            authorizer_id = _create_authorizer(api_id, authorizer)
            _authorizer_outputs[authorizer_id] = authorizer

        info['authorizers'] = _authorizer_outputs
        
    

    _stage_args = {
        "ApiId": info.get("cloud_id"),
        "AutoDeploy": True,
        "StageName": "live",
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
                search_name = None
                if resource.default_authorizer_name:
                    search_name = resource.default_authorizer_name

                if route.override_authorizer_name:
                    search_name = route.override_authorizer_name

                
                if search_name:
                    authorizer_id = [id for id, x in _authorizer_outputs.items() if x.name == search_name][0]

                else:
                    authorizer_id = None

                route_cloud_id = _create_route(api_id, route, authorizer_id)
            except Exception as e:
                output_task.print_error(e)
                raise e 


            # Add route to the return info
            dict_key = f'{route.path} {route.verb}'

            tmp = info.get("endpoints")

            tmp[dict_key] = route_cloud_id

            info["endpoints"] = tmp


    return info


def _update_simple_api(
    transaction_token: str, 
    namespace_token: str,
    previous_resource: simple_api.simple_api_model,
    new_resource: simple_api.simple_api_model,
    previous_output: frozendict,
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

    mutable_previous_output = dict(previous_output)
    previous_cloud_id = mutable_previous_output.get('cloud_id')

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


    if not previous_resource.routes == new_resource.routes:
        new_output_info = {}
        # Delete any route that is not in the new routes but in previous routes
        routes_to_be_deleted: FrozenSet[simple_api.route_model] = previous_resource.routes.difference(new_resource.routes)
        # Create any route that is in the new routes but not in previous routes
        routes_to_be_created: FrozenSet[simple_api.route_model] = new_resource.routes.difference(previous_resource.routes)

        
        for route in routes_to_be_created:

            output_task.update(advance=1, comment=f'Creating Route {route.path} [{route.verb}]')
            try:
                route_cloud_id = _create_route(previous_cloud_id, route)
            except Exception as e:
                output_task.print_error(e)
                raise e 


            dict_key = f'{route.path} {route.verb}'
            new_output_info[dict_key] = route_cloud_id



        previous_route_info: Dict[str,str] = dict(mutable_previous_output.get('endpoints'))


        for route in routes_to_be_deleted:
            dict_key = (
                f'{route.path} {route.verb}'
            )

            output_task.update(advance=1, comment=f'Deleting Route {route.path} [{route.verb}]')
            try:
                _delete_route(
                    previous_cloud_id, previous_route_info.get(dict_key)
                )
            except Exception as e:
                output_task.print_error(e)
                raise e 

            previous_route_info.pop(dict_key)


        previous_route_info.update(new_output_info)
        mutable_previous_output['endpoints'] = previous_route_info


    if not previous_resource.authorizers == new_resource.authorizers:
        # Three options for types of changes to authorizers
        # 1. Complete New 
        # 2. Complete Remove
        # 3. Update: This will show up as a delete and create when doing the set difference, so when going through the creates we 
        #    should look through the past authorizers to find one with the same name. 
        new_authorizer_info = {}
        previous_authorizers_info = dict(mutable_previous_output.get('authorizers'))
        updated = set()
        authorizers_to_delete: FrozenSet[simple_api.authorizer_model] = previous_resource.authorizers.difference(new_resource.authorizers)
        authorizers_to_create: FrozenSet[simple_api.authorizer_model] = new_resource.authorizers.difference(previous_resource.authorizers)

        for authorizer in authorizers_to_create:
            if any(x.name == authorizer.name for x in authorizers_to_delete):
                #update not hard create
                output_task.update(advance=1, comment=f'Updating Authorizer {authorizer.name}')
                
                authorizer_id = [id for id, v in previous_authorizers_info.items() if v.get("name") == authorizer.name][0]
                _update_authorizer(previous_output.get('cloud_id'), authorizer_id, authorizer)

                # Add this to updated authorizers so that it does not delete the authorizer in next steps
                updated.add(authorizer.name)
                # In the previous output, update the authorization info
                new_authorizer_info[authorizer_id] = authorizer

            else:
                output_task.update(advance=1, comment=f'Creating Authorizer {authorizer.name}')
                authorizer_id = _create_authorizer(previous_output.get('cloud_id'), authorizer)
                new_authorizer_info[authorizer_id] = authorizer

        

        for authorizer in authorizers_to_delete:
            if authorizer.name in updated:
                continue

            authorizer_id = [id for id, v in previous_authorizers_info.items() if v.get("name") == authorizer.name][0]
            output_task.update(advance=1, comment=f'Deleteing Authorizer {authorizer.name}')
            _delete_authorizer(previous_output.get('cloud_id'), authorizer_id)

            previous_authorizers_info.pop(authorizer_id)


        previous_authorizers_info.update(new_authorizer_info)
        mutable_previous_output['authorizers'] = previous_authorizers_info


    return mutable_previous_output


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


def _create_authorizer(api_id: str, authorizer: simple_api.authorizer_model) -> str:
    """Helper function for creating new authorizers

    Args:
        api_id (str): Api ID of the api in AWS.
        authorizer (simple_api.authorizer_model):Information about the authorizer to create

    Returns:
        str: Authorizer Id of the created Authorizer
    """
    args = {
        "ApiId": api_id,
        "Name": authorizer.name,
        "AuthorizerType": 'JWT',
        "IdentitySource":[
            '$request.header.Authorization',
        ],
        "JwtConfiguration": {
            'Audience': [
                authorizer.audience,
            ],
            "Issuer": authorizer.issuer_url
        }
    }

    rv = aws_client.run_client_function('apigatewayv2', 'create_authorizer', args)

    return rv.get("AuthorizerId")


def _update_authorizer(api_id: str, authorizer_id: str, authorizer: simple_api.authorizer_model):
    args = {
        "ApiId": api_id,
        "AuthorizerId": authorizer_id,
        "JwtConfiguration": {
            'Audience': [
                authorizer.audience,
            ],
            "Issuer": authorizer.issuer_url
        }
    }

    aws_client.run_client_function('apigatewayv2', 'update_authorizer', args)

def _delete_authorizer(api_id: str, authorizer_id: str):
    args = {
        "ApiId": api_id,
        "AuthorizerId": authorizer_id
    }
    aws_client.run_client_function('apigatewayv2', 'delete_authorizer', args)


def _create_route(api_id: str, route: simple_api.route_model, authorizer_id: str=None) -> str:
    """
    Helper Function for creating routes on an API. Note that any error raised by the aws client will not be caught by this function and should
    be handled by the caller of this function.

    Args:
        api_id (str): Api ID of the api in AWS.
        route (simple_api.route_event_model): Information about the route to create.

    Returns:
        str: Route ID of the create route.
    """

    full_args = {}
    _authorizer_args = {}

    _route_args = {
        "ApiId": api_id,
        "RouteKey": f"{route.verb} {route.path}",
    }

    if authorizer_id:
        _authorizer_args['AuthorizerId'] = authorizer_id
        _authorizer_args['AuthorizationType'] = 'JWT'
        
        if route.additional_scopes:
            _authorizer_args['AuthorizationScopes'] = route.additional_scopes
    

    full_args.update(_route_args)
    full_args.update(_authorizer_args)
    rv = aws_client.run_client_function('apigatewayv2', 'create_route', full_args)

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

