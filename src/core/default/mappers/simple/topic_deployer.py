from typing import Any, Dict
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.default.resources.simple import topic
from core.constructs.output_manager import OutputTask
from core.utils import hasher

from .. import aws_client


def _create_simple_topic(
    transaction_token: str,
    namespace_token: str,
    resource: topic.simple_topic_model,
    output_task: OutputTask,
) -> Dict:

    attributes = {}

    full_namespace_suffix = hasher.hash_list([namespace_token, str(uuid4())])

    topic_name = (
        f"cdev-topic-{full_namespace_suffix}.fifo"
        if resource.is_fifo
        else f"cdev-topic-{full_namespace_suffix}"
    )

    if resource.is_fifo:
        attributes.update({"FifoTopic": str(resource.is_fifo)})

    output_task.update(comment=f"Creating Topic {topic_name}")

    rv = aws_client.run_client_function(
        "sns", "create_topic", {"Name": topic_name, "Attributes": attributes}
    )

    output_info = {
        "topic_name": topic_name,
        "cdev_name": resource.name,
        "arn": rv.get("TopicArn"),
        "cloud_id": rv.get("TopicArn"),
    }

    return output_info


def _update_simple_topic(
    transaction_token: str,
    namespace_token: str,
    previous_resource: topic.simple_topic_model,
    new_resource: topic.simple_topic_model,
    previous_output: Dict,
    output_task: OutputTask,
) -> Dict:
    _remove_simple_topic(transaction_token, previous_output, output_task)
    new_rv = _create_simple_topic(
        transaction_token, namespace_token, new_resource, output_task
    )
    return new_rv


def _remove_simple_topic(
    transaction_token: str, previous_output: Dict, output_task: OutputTask
) -> None:
    topic_arn = previous_output.get("cloud_id")

    aws_client.run_client_function("sns", "delete_topic", {"TopicArn": topic_arn})


def add_subscriber(topic_arn: str, protocol: str, endpoint: str) -> str:
    rv = aws_client.run_client_function(
        "sns",
        "subscribe",
        {
            "TopicArn": topic_arn,
            "Protocol": protocol,
            "Endpoint": endpoint,
            "ReturnSubscriptionArn": True,
        },
    )

    return rv.get("SubscriptionArn")


def remove_subscriber(subscription_arn: str) -> None:
    rv = aws_client.run_client_function(
        "sns", "unsubscribe", {"SubscriptionArn": subscription_arn}
    )


def handle_simple_topic_deployment(
    transaction_token: str,
    namespace_token: str,
    resource_diff: Resource_Difference,
    previous_output: Dict[str, Any],
    output_task: OutputTask,
) -> Dict:
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        return _create_simple_topic(
            transaction_token, namespace_token, resource_diff.new_resource, output_task
        )

    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
        return _update_simple_topic(
            transaction_token,
            namespace_token,
            topic.simple_topic_model(**resource_diff.previous_resource.dict()),
            resource_diff.new_resource,
            previous_output,
            output_task,
        )

    elif resource_diff.action_type == Resource_Change_Type.DELETE:
        _remove_simple_topic(transaction_token, previous_output, output_task)

        return {}
