from typing import Any, Dict, FrozenSet, List, Tuple, Optional
from uuid import uuid4
from core.constructs.models import frozendict

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.constructs.output_manager import OutputTask
from core.default.resources.simple import api as simple_api

from .. import aws_client


class NoAuthorizerIdFoundError(Exception):
    pass


default_cors_args = {
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


def _create_simple_api(
    transaction_token: str,
    namespace_token: str,
    resource: simple_api.simple_api_model,
    output_task: OutputTask,
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

    api_args = {
        "Name": f"cdev-api-{namespace_token}-{str(uuid4())}",
        "ProtocolType": "HTTP",
        "CorsConfiguration": default_cors_args if resource.allow_cors else {},
        "Tags": dict(resource.tags) if resource.tags else {},
    }

    output_task.update(advance=1, comment="Creating Api")

    try:
        rv = aws_client.run_client_function("apigatewayv2", "create_api", api_args)
    except Exception as e:
        output_task.print_error(e)
        raise e

    api_id = rv.get("ApiId")

    info = {
        "cloud_id": api_id,
        "endpoints": {},
    }

    if resource.authorizers:
        info["authorizers"] = _create_authorizers(api_id, resource, output_task)

    info["endpoint"] = _create_stage(
        api_id, rv.get("ApiEndpoint"), resource, output_task
    )

    if resource.routes:
        info["endpoints"] = _create_routes(
            api_id, info.get("authorizers"), resource, output_task
        )

    return info


def _update_simple_api(
    transaction_token: str,
    namespace_token: str,
    previous_resource: simple_api.simple_api_model,
    new_resource: simple_api.simple_api_model,
    previous_output: frozendict,
    output_task: OutputTask,
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
    previous_cloud_id = mutable_previous_output.get("cloud_id")

    output_task.print(previous_resource)

    # Change the CORS Settings of the API
    if (
        previous_resource.allow_cors != new_resource.allow_cors
        or previous_resource.tags != new_resource.tags
    ):
        api_args = {
            "ApiId": previous_cloud_id,
            # "Tags": dict(new_resource.tags) if new_resource.tags else [],
            "CorsConfiguration": default_cors_args if new_resource.allow_cors else {},
        }

        output_task.update(advance=1, comment=f"Updating CORS Policy and tags")
        try:
            aws_client.run_client_function(
                "apigatewayv2",
                "update_api",
                api_args,
            )
        except Exception as e:
            output_task.print_error(e)
            raise e

    # If an authorizer is to be deleted, it must already be removed from any route but,
    # to create a route with an authorizer, you must have already created the authorizer.
    # This means we can NOT do all the operations on the routes before authorizers but also can NOT do all
    # the authorizers before the routes.

    # We must do them in an order that does not cause errors, so we are only going to perform update operations
    # that must happen before the authorizers are updated then defer the rest of the updates till after by storing
    # their info in the `_update_route_info` and `_create_route_info` list.
    _create_route_info: List[simple_api.route_model] = []
    _update_route_info: List[Tuple[str, simple_api.route_model]] = []
    previous_route_info: Dict[str, str] = (
        dict(mutable_previous_output.get("endpoints"))
        if mutable_previous_output.get("endpoints")
        else {}
    )
    new_output_info = {}

    if previous_resource.routes != new_resource.routes:

        update_routes = set()

        # Delete any route that is not in the new routes but in previous routes
        routes_to_be_deleted: FrozenSet[
            simple_api.route_model
        ] = previous_resource.routes.difference(new_resource.routes)
        # Create any route that is in the new routes but not in previous routes
        routes_to_be_created: FrozenSet[
            simple_api.route_model
        ] = new_resource.routes.difference(previous_resource.routes)

        previous_route_ids = set(
            [f"{x.path} {x.verb}" for x in previous_resource.routes]
        )

        for route in routes_to_be_created:
            route_id = f"{route.path} {route.verb}"

            if route_id in previous_route_ids:
                # This is updating the routes authorization not making a new route
                # There are a few states that require making an update to the current route before the authorizers are updated.
                # Updating to a new Authorizer
                #      - Previous Authorizer was none -> No update needed
                #      - Previous Authorizer existed -> remove the authorizer from the route

                update_routes.add(route_id)

                route_cloud_id = previous_route_info.get(route_id)

                if not mutable_previous_output.get("authorizers"):
                    # No previous authorization info means all route updates should wait til authorizations
                    # have completed
                    _update_route_info.append((route_cloud_id, route))
                    continue

                # guranteed to have an element because the invariant of the if statement
                previous_route = [
                    x
                    for x in previous_resource.routes
                    if f"{x.path} {x.verb}" == route_id
                ][0]

                # Find the previous id... we have to pass in the previous api since that was used in the previous computation regarding
                # the default authorizer
                try:
                    previous_authorizer_id = _find_authorization_id(
                        previous_route, mutable_previous_output.get("authorizers")
                    )
                except NoAuthorizerIdFoundError as e:
                    # If a previous authorizer was to be found and it wasn't then there is something wrong since we should have all the info on previous
                    # authorizers
                    raise e

                if previous_authorizer_id:
                    # remove the previous authorizer, but defer the updating to the new one until after authorizers have finished
                    print(f"soft update {route}")
                    _update_route(previous_cloud_id, route_cloud_id, route, None)
                    _update_route_info.append((route_cloud_id, route))

                else:
                    # 1A
                    # No previous authorizer so wait til after to complete the authorization
                    _update_route_info.append((route_cloud_id, route))

            else:
                # All creates should just happen after the authorizers have been made
                _create_route_info.append(route)

        for route in routes_to_be_deleted:
            # All deletes should go ahead and occur now
            route_id = f"{route.path} {route.verb}"

            if route_id in update_routes:
                continue

            output_task.update(
                advance=1, comment=f"Deleting Route {route.path} [{route.verb}]"
            )
            try:
                _delete_route(previous_cloud_id, previous_route_info.get(route_id))
            except Exception as e:
                output_task.print_error(e)
                print(
                    f"error deleting {previous_cloud_id} -> {previous_route_info.get(route_id)}"
                )
                raise e

            previous_route_info.pop(route_id)

    if previous_resource.authorizers != new_resource.authorizers:
        # Three options for types of changes to authorizers
        # 1. Complete New
        # 2. Complete Remove
        # 3. Update: This will show up as a delete and create when doing the set difference, so when going through the creates we
        #    should look through the past authorizers to find one with the same name.
        new_authorizer_info = {}
        previous_authorizers_info = (
            dict(mutable_previous_output.get("authorizers"))
            if mutable_previous_output.get("authorizers")
            else {}
        )
        updated = set()

        authorizers_to_delete: FrozenSet[
            simple_api.authorizer_model
        ] = previous_resource.authorizers.difference(new_resource.authorizers)
        authorizers_to_create: FrozenSet[
            simple_api.authorizer_model
        ] = new_resource.authorizers.difference(previous_resource.authorizers)

        for authorizer in authorizers_to_create:
            if any(x.name == authorizer.name for x in authorizers_to_delete):
                # update not hard create
                output_task.update(
                    advance=1, comment=f"Updating Authorizer {authorizer.name}"
                )

                authorizer_id = [
                    id
                    for id, v in previous_authorizers_info.items()
                    if v.get("name") == authorizer.name
                ][0]
                _update_authorizer(
                    previous_output.get("cloud_id"), authorizer_id, authorizer
                )

                # Add this to updated authorizers so that it does not delete the authorizer in next steps
                updated.add(authorizer.name)
                # In the previous output, update the authorization info
                new_authorizer_info[authorizer_id] = authorizer.dict()

            else:
                output_task.update(
                    advance=1, comment=f"Creating Authorizer {authorizer.name}"
                )
                authorizer_id = _create_authorizer(
                    previous_output.get("cloud_id"), authorizer
                )
                new_authorizer_info[authorizer_id] = authorizer.dict()

        for authorizer in authorizers_to_delete:
            if authorizer.name in updated:
                continue

            authorizer_id = [
                id
                for id, v in previous_authorizers_info.items()
                if v.get("name") == authorizer.name
            ][0]
            output_task.update(
                advance=1, comment=f"Deleteing Authorizer {authorizer.name}"
            )
            _delete_authorizer(previous_output.get("cloud_id"), authorizer_id)

            previous_authorizers_info.pop(authorizer_id)

        previous_authorizers_info.update(new_authorizer_info)
        mutable_previous_output["authorizers"] = previous_authorizers_info

    for route in _create_route_info:
        # Now that all updates to the authorizers have completed, we can do the create routes
        route_id = f"{route.path} {route.verb}"

        # Find the authorizer id
        authorizer_id = _find_authorization_id(
            route, mutable_previous_output.get("authorizers")
        )

        output_task.update(
            advance=1, comment=f"Creating Route {route.path} [{route.verb}]"
        )

        route_cloud_id = _create_route(previous_cloud_id, route, authorizer_id)

        new_output_info[route_id] = route_cloud_id

    for id, route in _update_route_info:
        # Now that all updates to the authorizers have completed, we can do the update routes that depends on the created
        # authorization
        route_id = f"{route.path} {route.verb}"

        # Find the authorizer id
        authorizer_id = _find_authorization_id(
            route, mutable_previous_output.get("authorizers")
        )

        output_task.update(
            advance=1, comment=f"Updating Route {route.path} [{route.verb}]"
        )

        _update_route(previous_cloud_id, id, route, authorizer_id)

    previous_route_info.update(new_output_info)
    mutable_previous_output["endpoints"] = previous_route_info

    return mutable_previous_output


def _remove_simple_api(
    transaction_token: str, previous_output: Dict, output_task: OutputTask
) -> None:
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

    output_task.update(advance=1, comment=f"Deleting API")

    try:
        aws_client.run_client_function("apigatewayv2", "delete_api", {"ApiId": api_id})
    except Exception as e:
        output_task.print_error(e)
        raise e


def _create_authorizers(
    api_id: str, resource: simple_api.simple_api_model, output_task: OutputTask
) -> Dict[str, Dict]:
    authorizers_created: Dict[str, Dict] = {}

    for authorizer in resource.authorizers:
        output_task.update(advance=1, comment=f"Creating Authorizer {authorizer.name}")
        authorizer_id = _create_authorizer(api_id, authorizer)
        authorizers_created[authorizer_id] = authorizer.dict()

    return authorizers_created


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
        "AuthorizerType": "JWT",
        "IdentitySource": [
            "$request.header.Authorization",
        ],
        "JwtConfiguration": {
            "Audience": [
                authorizer.audience,
            ],
            "Issuer": authorizer.issuer_url,
        },
    }

    rv = aws_client.run_client_function("apigatewayv2", "create_authorizer", args)

    return rv.get("AuthorizerId")


def _update_authorizer(
    api_id: str, authorizer_id: str, authorizer: simple_api.authorizer_model
):
    args = {
        "ApiId": api_id,
        "AuthorizerId": authorizer_id,
        "JwtConfiguration": {
            "Audience": [
                authorizer.audience,
            ],
            "Issuer": authorizer.issuer_url,
        },
    }

    aws_client.run_client_function("apigatewayv2", "update_authorizer", args)


def _delete_authorizer(api_id: str, authorizer_id: str) -> None:
    args = {"ApiId": api_id, "AuthorizerId": authorizer_id}
    aws_client.run_client_function("apigatewayv2", "delete_authorizer", args)


def _find_authorization_id(
    route: simple_api.route_model, output_ids: Dict[str, Dict]
) -> Optional[str]:
    """Function for finding a route's authorizer cloud id

    This function takes into account that a route will by default use the api's default authorizer unless the route has the `override_authorizer_name`
    set. Will return None if the route will not have an authorizer or there is not enough information to find the authorizer.

    Args:
        api_resource (simple_api.simple_api_model): _description_
        route (simple_api.route_model): _description_
        output_ids (Dict[str, Dict]): _description_

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        str: _description_
    """

    if not route.authorizer_name:
        return None

    if not output_ids:
        return None

    found_id = [
        id for id, x in output_ids.items() if x.get("name") == route.authorizer_name
    ]

    if len(found_id) == 0 and route.authorizer_name:
        # We have an authorizer but can not find the info for it
        raise NoAuthorizerIdFoundError

    if len(found_id) > 1:
        raise Exception

    return found_id[0]


def _create_stage(
    cloud_id: str,
    api_endpoint: str,
    resource: simple_api.simple_api_model,
    output_task: OutputTask,
) -> str:

    stage_args = {
        "ApiId": cloud_id,
        "AutoDeploy": True,
        "StageName": "live",
        "Tags": dict(resource.tags) if resource.tags else {},
    }

    stage: str
    output_task.update(advance=1, comment="Creating Stage")
    try:
        rv2 = aws_client.run_client_function("apigatewayv2", "create_stage", stage_args)
        stage = f"{api_endpoint}/{rv2.get('StageName')}"
    except Exception as e:
        output_task.print_error(e)
        raise e
    return stage


def _create_routes(
    cloud_id: str,
    authorizers,
    resource: simple_api.simple_api_model,
    output_task: OutputTask,
) -> Dict[str, str]:

    created_endpoints = {}
    for route in resource.routes:
        output_task.update(
            advance=1, comment=f"Creating Route {route.path} [{route.verb}]"
        )

        try:
            authorizer_id = _find_authorization_id(route, authorizers)
            route_cloud_id = _create_route(cloud_id, route, authorizer_id)
            # Add route to the return info
            created_endpoints[f"{route.path} {route.verb}"] = route_cloud_id
        except Exception as e:
            output_task.print_error(e)
            raise e

    return created_endpoints


def _create_route(
    api_id: str, route: simple_api.route_model, authorizer_id: str = None
) -> str:
    """
    Helper Function for creating routes on an API. Note that any error raised by the aws client will not be caught by this function and should
    be handled by the caller of this function.

    Args:
        api_id (str): Api ID of the api in AWS.
        route (simple_api.route_event_model): Information about the route to create.

    Returns:
        str: Route ID of the create route.
    """
    route_args = {
        "ApiId": api_id,
        "RouteKey": f"{route.verb} {route.path}",
    }

    if authorizer_id:
        route_args["AuthorizerId"] = authorizer_id
        route_args["AuthorizationType"] = "JWT"

        if route.additional_scopes:
            route_args["AuthorizationScopes"] = list(route.additional_scopes)

    rv = aws_client.run_client_function("apigatewayv2", "create_route", route_args)
    return rv.get("RouteId")


def _delete_route(api_id: str, route_id: str) -> None:
    """
    Helper Function for deleting routes on an API. Note that any error raised by the aws client will not be caught by this function and should
    be handled by the caller of this function.

    Args:
        api_id (str): Api ID of the api in AWS.
        route_id (lambda_event): Route ID of the route in AWS.
    """
    print(f">>> {route_id}")
    aws_client.run_client_function(
        "apigatewayv2", "delete_route", {"ApiId": api_id, "RouteId": route_id}
    )


def _update_route(
    api_id: str, route_id: str, route: simple_api.route_model, authorizer_id: str = None
):

    route_args = {
        "ApiId": api_id,
        "RouteId": route_id,
    }

    if authorizer_id:
        route_args["AuthorizerId"] = authorizer_id
        route_args["AuthorizationType"] = "JWT"

        if route.additional_scopes:
            route_args["AuthorizationScopes"] = list(route.additional_scopes)
        else:
            route_args["AuthorizationScopes"] = []
    else:
        route_args["AuthorizerId"] = ""
        route_args["AuthorizationType"] = "NONE"
        route_args["AuthorizationScopes"] = []

    aws_client.run_client_function("apigatewayv2", "update_route", route_args)


def handle_simple_api_deployment(
    transaction_token: str,
    namespace_token: str,
    resource_diff: Resource_Difference,
    previous_output: Dict[str, Any],
    output_task: OutputTask,
) -> Dict:

    result: Dict = {}
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        result = _create_simple_api(
            transaction_token, namespace_token, resource_diff.new_resource, output_task
        )

    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
        result = _update_simple_api(
            transaction_token,
            namespace_token,
            simple_api.simple_api_model(**resource_diff.previous_resource.dict()),
            resource_diff.new_resource,
            previous_output,
            output_task,
        )

    elif resource_diff.action_type == Resource_Change_Type.DELETE:
        _remove_simple_api(transaction_token, previous_output, output_task)

    return result
