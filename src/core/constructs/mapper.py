"""Structure that deploys the resources onto the cloud

"""

from typing import Dict, List, Set, Callable

from .resource import Resource_Difference

from core.constructs.output_manager import OutputTask


class CloudMapper:
    """
    A Cloud Mapper is the construct responsible for directly interacting with the Cloud Provider and managing resource state.
    """

    def __init__(self, resource_to_handler: Dict[str, Callable]) -> None:
        self.resource_to_handler = resource_to_handler

    def get_namespaces(self) -> List[str]:
        """Get the available ruuid that this mapper supports

        Raises:
            NotImplementedError

        Returns:
            Set[str]
        """
        raise NotImplementedError

    def deploy_resource(
        self,
        transaction_token: str,
        namespace_token: str,
        resource_diff: Resource_Difference,
        previous_output: Dict,
        output_task: OutputTask,
    ) -> Dict:
        """Deploy a given resource difference

        Args:
            transaction_token (str): The transaction token
            namespace_token (str): The namespace token
            resource_diff (Resource_Difference): resource diff
            previous_output (Dict): previous output from cloud
            output_task (OutputTask): task to update

        Raises:
            NotImplementedError

        Returns:
            Dict
        """
        raise NotImplementedError

    def get_available_resources(self) -> Set[str]:
        """Get the available ruuid that this mapper supports

        Raises:
            NotImplementedError

        Returns:
            Set[str]
        """
        raise NotImplementedError

    def get_resource_to_handler(self) -> Dict[str, Callable]:
        """Get the exact mapper for each resource

        Raises:
            NotImplementedError

        Returns:
            Set[str]
        """
        raise NotImplementedError
