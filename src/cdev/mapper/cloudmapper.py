from typing import List


from cdev.models import Action_Type, Resource_State_Difference
from cdev.constructs import CloudMapper
from cdev.settings import SETTINGS

from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .backend.aws import aws_lambda, aws_dynamodb


class DefaultMapper(CloudMapper):
    """
    This is the class documentation 

    ---------------------------------
    """
    def __init__(self) -> None:
        super().__init__(RESOURCE_TO_HANDLER_FUNCTION,RESOURCE_TO_OUTPUT_RENDERER)

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
            resource_diff.new_resource = self.get_resource_to_output_renderer()[resource_diff.new_resource.ruuid](resource_diff.new_resource)
        
        return resource_diff


def dynamodb_replace_output(resource):
    return resource


RESOURCE_TO_HANDLER_FUNCTION = {
    "cdev::aws::lambda_function": aws_lambda.handle_aws_lambda_deployment,
    "cdev::aws::dynamodb": aws_dynamodb.handle_dynamodb_deployment
}

RESOURCE_TO_OUTPUT_RENDERER = {
    "cdev::aws::lambda_function": aws_lambda.lambda_replace_output,
    "cdev::aws::dynamodb": dynamodb_replace_output
}
