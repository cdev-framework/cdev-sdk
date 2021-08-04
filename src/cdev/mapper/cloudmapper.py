from typing import List

from cdev.models import Action_Type, Resource_State_Difference
from cdev.constructs import CloudMapper
from cdev.settings import SETTINGS

from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .backend.aws import aws_lambda, dynamodb, iam, s3, sqs, apigatewayv2


class DefaultMapper(CloudMapper):
    """
    This is the class documentation 

    ---------------------------------
    """
    def __init__(self) -> None:
        super().__init__(RESOURCE_TO_HANDLER_FUNCTION)

    def get_namespaces(self) -> List[str]:
        return ["cdev"]

    def deploy_resource(self, resource_diff: Resource_State_Difference) -> bool:
        if not resource_diff.action_type == Action_Type.DELETE:
            if not resource_diff.new_resource.ruuid in self.get_resource_to_handler():
                # TODO throw error
                print(f"PROVIDER CAN NOT CREATE RESOURCE: {resource_diff.new_resource.ruuid}")

            self.get_resource_to_handler()[resource_diff.new_resource.ruuid](resource_diff)

        else:
            self.get_resource_to_handler()[resource_diff.previous_resource.ruuid](resource_diff)

        return True

    def render_resource_outputs(self, resource_diff)-> Resource_State_Difference:
        if resource_diff.new_resource:

            replaced_output = replace_output(resource_diff.new_resource.dict())
           
            resource_diff.new_resource = type(resource_diff.new_resource).parse_obj(replaced_output)
        return resource_diff




def replace_output(obj) -> dict:

    rv = _recursive_replace_output(obj)

    return rv


def _recursive_replace_output(obj) -> dict:
    rv = dict()

    if isinstance(obj, dict): 
        for k,v in obj.items():
            if isinstance(v, dict):
                if "type" in v and v.get("type") == 'cdev_output':
                  
                    identifier = v.get('resource').split("::")[-1]
                    rv[k] = cdev_cloud_mapper.get_output_value(identifier, v.get("key"))

                else:
                    rv[k] = _recursive_replace_output(v)

            elif isinstance(v, list):
                rv[k] = [_recursive_replace_output(x) for x in v]

            else:
                rv[k] = v

        return rv

    elif isinstance(obj, list):
        return [_recursive_replace_output(x) for x in obj]

    else:
        return obj

    




RESOURCE_TO_HANDLER_FUNCTION = {
    "cdev::aws::lambda_function": aws_lambda.handle_aws_lambda_deployment,
    "cdev::aws::dynamodb::table": dynamodb.handle_table_deployment,
    "cdev::aws::iam::policy": iam.handle_policy_deployment,
    "cdev::aws::iam::role": iam.handle_role_deployment,
    "cdev::aws::s3::bucket": s3.handle_bucket_deployment,
    "cdev::aws::sqs::queue": sqs.handle_queue_deployment,
    "cdev::aws::apigatewayv2::api": apigatewayv2.handle_api_deployment,
    "cdev::aws::apigatewayv2::route": apigatewayv2.handle_route_deployment,
    "cdev::aws::apigatewayv2::integration": apigatewayv2.handle_integration_deployment
}

