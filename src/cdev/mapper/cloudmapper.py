from typing import List


from cdev.models import Action_Type, Resource_State_Difference
from cdev.constructs import CloudMapper
from cdev.settings import SETTINGS

from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .backend.aws import aws_lambda


class DefaultMapper(CloudMapper):
    def __init__(self) -> None:
        super().__init__(RESOURCE_TO_HANDLER_FUNCTION)

    def get_namespaces(self) -> List[str]:
        return ["cdev"]

    def deploy_resource(self, resource_diff: Resource_State_Difference) -> Resource_State_Difference:
        
        
        if not resource_diff.action_type == Action_Type.DELETE:
            if not resource_diff.new_resource.ruuid in self.get_resource_to_handler():
                # TODO throw error
                print(f"PROVIDER CAN NOT CREATE RESOURCE: {resource_diff.new_resource.ruuid}")

            self.get_resource_to_handler()[resource_diff.new_resource.ruuid](resource_diff)

        else:
            self.get_resource_to_handler()[resource_diff.previous_resource.ruuid](resource_diff)

        #print(f"DEPLOYING -> {resource_diff}")

        return True
    

def handle_aws_dynamodb_deployment(resource_diff: Resource_State_Difference):
    # TODO throw error if resource is not lambda function
    if resource_diff.action_type == Action_Type.CREATE:
        cdev_cloud_mapper.add_cloud_resource(resource_diff.new_resource.hash, {"s3key": resource_diff.new_resource.TableName})
    
    #print(f"DYNAMODB {resource_diff}")


RESOURCE_TO_HANDLER_FUNCTION = {
    "cdev::aws::lambda_function": aws_lambda.handle_aws_lambda_deployment,
    "cdev::aws::dynamodb": handle_aws_dynamodb_deployment
}
