from typing import Any, Dict
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.default.resources.simple import queue
from core.constructs.output_manager import OutputTask
from core.utils import hasher

from .. import aws_client


def _create_simple_queue(
    transaction_token: str,
    namespace_token: str,
    resource: queue.queue_model,
    output_task: OutputTask,
) -> Dict:

    attributes = {}

    full_namespace_suffix = hasher.hash_list([namespace_token, str(uuid4())])

    queue_name = (
        f"cdev-queue-{full_namespace_suffix}.fifo"
        if resource.is_fifo
        else f"cdev-queue-{full_namespace_suffix}"
    )

    if resource.is_fifo:
        attributes.update({"FifoQueue": str(resource.is_fifo)})

    output_task.update(comment=f"Creating Queue {queue_name}")

    rv = aws_client.run_client_function(
        "sqs",
        "create_queue",
        {"QueueName": queue_name, "Attributes": attributes},
    )

    output_info = {
        "queue_name": queue_name,
        "cdev_name": resource.name,
        "queue_url": rv.get("QueueUrl"),
    }

    # rv does not contain the arn of the queue so we need a second call

    rv = aws_client.run_client_function(
        "sqs",
        "get_queue_attributes",
        {"QueueUrl": output_info.get("queue_url"), "AttributeNames": ["QueueArn"]},
    )

    output_info.update(
        {
            "cloud_id": rv.get("Attributes").get("QueueArn"),
            "arn": rv.get("Attributes").get("QueueArn"),
        }
    )

    return output_info


def _update_simple_queue(
    transaction_token: str,
    namespace_token: str,
    previous_resource: queue.queue_model,
    new_resource: queue.queue_model,
    previous_output: Dict,
    output_task: OutputTask,
) -> Dict:
    _remove_simple_queue(transaction_token, previous_output, output_task)
    new_info = _create_simple_queue(
        transaction_token, namespace_token, new_resource, output_task
    )
    return new_info


def _remove_simple_queue(
    transaction_token: str, previous_output: Dict, output_task: OutputTask
) -> None:
    queue_url = previous_output.get("queue_url")

    output_task.update(comment=f"Deleting Queue")

    aws_client.run_client_function("sqs", "delete_queue", {"QueueUrl": queue_url})


def handle_simple_queue_deployment(
    transaction_token: str,
    namespace_token: str,
    resource_diff: Resource_Difference,
    previous_output: Dict[str, Any],
    output_task: OutputTask,
) -> Dict:
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        return _create_simple_queue(
            transaction_token, namespace_token, resource_diff.new_resource, output_task
        )

    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
        return _update_simple_queue(
            transaction_token,
            namespace_token,
            queue.queue_model(**resource_diff.previous_resource.dict()),
            resource_diff.new_resource,
            previous_output,
            output_task,
        )

    elif resource_diff.action_type == Resource_Change_Type.DELETE:
        _remove_simple_queue(transaction_token, previous_output, output_task)

        return {}
