from typing import List

from cdev.models import Resource_State_Difference
from cdev.constructs import CloudMapper

class DefaultMapper(CloudMapper):
    def __init__(self) -> None:
        pass

    def get_namespaces(self) -> List[str]:
        return ["cdev"]

    def deploy_resource(self, component_name: str, resource_diff: Resource_State_Difference) -> Resource_State_Difference:
        return resource_diff
