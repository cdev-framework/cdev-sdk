"""Structure that deploys the resources onto the cloud 

"""

from typing import Dict, Union, List, Optional, Set, Callable

from .resource import Resource_Difference

from core.constructs.output_manager import OutputTask


class CloudMapper:
    """
    A Cloud Mapper is the construct responsible for directly interacting with the Cloud Provider and managing resource state.
    """

    def __init__(self, resource_to_handler: Dict[str, Callable]) -> None:
        self.resource_to_handler = resource_to_handler

    def get_namespaces(self) -> List[str]:
        raise NotImplementedError

    def deploy_resource(self, transaction_token: str, namespace_token: str, resource_diff: Resource_Difference, previous_output: Dict, output_task: OutputTask) -> Dict:
        raise NotImplementedError

    def get_available_resources(self) -> Set[str]:
        raise NotImplementedError

    def get_resource_to_handler(self) -> Dict[str, Callable]:
        raise NotImplementedError

