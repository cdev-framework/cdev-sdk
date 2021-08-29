from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import api as simple_api
from cdev.resources.aws import apigatewayv2_models
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from ..aws import apigatewayv2 as apigatewayv2_deployer


log = logger.get_cdev_logger(__name__)


def create_simple_api(identifier: str, resource: simple_api.simple_api_model) -> bool:

    # First create the API Gateway V2 resource

    _api_model = apigatewayv2_models.api_model(
        **{
            "ruuid": "",
            "hash": "",
            "name": "",
            "Name": resource.api_name,
            "ProtocolType": apigatewayv2_models.ProtocolType.HTTP,
        }
    )

    rv = apigatewayv2_deployer._create_api("", _api_model)
    log.info(rv)



    info = {
        
        "endpoint": rv.get("ApiEndpoint"),
        "cloud_id": rv.get("ApiId"),
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

    log.info(rv2)

    info['base_endpoint'] = f"{rv.get('ApiEndpoint')}/{rv2.get('StageName')}"

    if resource.routes:
        for route in resource.routes:
           
            _route_model = apigatewayv2_models.route_model(
                **{
                    "ruuid": "",
                    "hash": "",
                    "name": "",
                    "ApiId": info.get("cloud_id"),
                    "RouteKey": f"{route.config.get('verb')} {route.config.get('path')}"
                }
            )

            tmp_rv = apigatewayv2_deployer._create_route("", _route_model)

            log.info(tmp_rv)

            route_info = {
                "cloud_id": tmp_rv.get("RouteId"),
                "route": route.config.get("path"),
                "verbs": route.config.get("verb")
            }

            dict_key = f'{route.config.get("path")}:{route.config.get("verb")}'

            tmp =  info.get('endpoints')
            tmp[dict_key] = route_info

            info['endpoints'] = tmp



    cdev_cloud_mapper.add_cloud_resource(identifier, resource)
    cdev_cloud_mapper.update_output_value(identifier, info)

    return True



def remove_simple_api(identifier: str, resource: simple_api.simple_api_model) -> bool:
    pass




def handle_simple_api_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:

            return create_simple_api(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return True
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return remove_simple_api(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
