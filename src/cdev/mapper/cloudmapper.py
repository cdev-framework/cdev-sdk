from typing import List

from cdev.models import Action_Type, Resource_State_Difference
from cdev.constructs import CloudMapper




class DefaultMapper(CloudMapper):
    def __init__(self) -> None:
        super().__init__(RESOURCE_TO_HANDLER_FUNCTION)

    def get_namespaces(self) -> List[str]:
        return ["cdev"]

    def deploy_resource(self, component_name: str, resource_diff: Resource_State_Difference) -> Resource_State_Difference:
        
        
        if not resource_diff.action_type == Action_Type.DELETE:
            if not resource_diff.new_resource.ruuid in self.get_resource_to_handler():
                # TODO throw error
                print(f"PROVIDER CAN NOT CREATE RESOURCE: {resource_diff.new_resource.ruuid}")

        print(f"DEPLOYING -> {component_name}:{resource_diff}")
        self.get_resource_to_handler()[resource_diff.new_resource.ruuid](component_name, resource_diff)

        return True


def handle_aws_lambda_deployment(component_name: str, resource_diff):
    # TODO throw error if resource is not lambda function

    print(resource_diff)



def handle_aws_dynamodb_deployment(component_name: str, resource_diff):
    # TODO throw error if resource is not lambda function

    print(f"DYNAMODB {resource_diff}")


RESOURCE_TO_HANDLER_FUNCTION = {
    "cdev::general::parsed_function": handle_aws_lambda_deployment,
    "cdev::aws::dynamodb": handle_aws_dynamodb_deployment
}
