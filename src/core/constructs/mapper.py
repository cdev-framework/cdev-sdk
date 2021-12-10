from typing import Dict, Union, List, Optional, Set, Callable

from .resource import Resource_Difference

class CloudMapper():
    """
    A Cloud Mapper is the construct responsible for directly interacting with the Cloud Provider and managing resource state. 
    """
    def __init__(self, resource_to_handler: Dict[str, Callable]) -> None:
        self.resource_to_handler = resource_to_handler
        pass

    def get_namespaces(self) -> List[str]:
        pass

    def deploy_resource(self, resource_diff: Resource_Difference) -> bool:
        pass

    def get_available_resources(self) -> Set[str]:
        pass

    def get_resource_to_handler(self) -> Dict[str, Callable]:
        pass

    def render_resource_outputs(self, resource_diff: Resource_Difference) -> Resource_Difference:
        pass