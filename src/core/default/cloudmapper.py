from typing import Callable, Dict, List, Set


from core.constructs.output_manager import OutputTask
from core.constructs.resource import Resource_Difference
from core.constructs.mapper import CloudMapper

from .mappers.simple import (
    api_deployer,
    bucket_deployer,
    lambda_deployer,
    dynamodb_deployer,
    queue_deployer,
    relational_db_deployer,
    static_site_deployer,
    topic_deployer,
)


class DefaultMapper(CloudMapper):
    def __init__(self) -> None:
        super().__init__(RESOURCE_TO_HANDLER_FUNCTION)

    def get_namespaces(self) -> List[str]:
        return [
            "cdev::simple::api",
            "cdev::simple::bucket",
            "cdev::simple::function",
            "cdev::simple::lambda_layer",
            "cdev::simple::table",
            "cdev::simple::queue",
            "cdev::simple::relationaldb",
            "cdev::simple::staticsite",
            "cdev::simple::topic",
        ]

    def deploy_resource(
        self,
        transaction_token: str,
        namespace_token: str,
        resource_diff: Resource_Difference,
        previous_output: Dict,
        output_task: OutputTask,
    ) -> Dict:
        ruuid = (
            resource_diff.new_resource.ruuid
            if resource_diff.new_resource
            else resource_diff.previous_resource.ruuid
        )

        return self.get_resource_to_handler()[ruuid](
            transaction_token,
            namespace_token,
            resource_diff,
            previous_output,
            output_task,
        )

    def get_available_resources(self) -> Set[str]:
        return set(self.get_namespaces())

    def get_resource_to_handler(self) -> Dict[str, Callable]:
        return self.resource_to_handler


RESOURCE_TO_HANDLER_FUNCTION = {
    "cdev::simple::function": lambda_deployer.handle_simple_lambda_function_deployment,
    "cdev::simple::lambda_layer": lambda_deployer.handle_simple_layer_deployment,
    "cdev::simple::api": api_deployer.handle_simple_api_deployment,
    "cdev::simple::bucket": bucket_deployer.handle_simple_bucket_deployment,
    "cdev::simple::table": dynamodb_deployer.handle_simple_table_deployment,
    "cdev::simple::queue": queue_deployer.handle_simple_queue_deployment,
    "cdev::simple::relationaldb": relational_db_deployer.handle_simple_relational_db_deployment,
    "cdev::simple::staticsite": static_site_deployer.handle_simple_static_site_deployment,
    "cdev::simple::topic": topic_deployer.handle_simple_topic_deployment,
}
