from typing import List

from cdev.models import Resource_State_Difference
from cdev.constructs import CloudMapper


AVAILABLE_RESOURCES = [
    "cdev::aws::dynamodb",
    "cdev::general::parsed_function"
]

class DefaultMapper(CloudMapper):
    def __init__(self) -> None:
        super().__init__(set(AVAILABLE_RESOURCES))

    def get_namespaces(self) -> List[str]:
        return ["cdev"]

    def deploy_resource(self, component_name: str, resource_diff: Resource_State_Difference) -> Resource_State_Difference:
        if not resource_diff.new_resource.ruuid in self.resources:
            # TODO throw error
            print(f"PROVIDER CAN NOT CREATE RESOURCE: {resource_diff.new_resource.ruuid}")

        print(f"DEPLOYING -> {component_name}:{resource_diff}")


        return resource_diff
