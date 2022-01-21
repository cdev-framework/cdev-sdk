from enum import Enum
from types import new_class
from typing import Dict, List

from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import hasher, logger
from cdev.resources.simple import queue as simple_queue
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from ..aws import aws_client as raw_aws_client
from cdev.output import print_deployment_step

log = logger.get_cdev_logger(__name__)
RUUID = simple_queue.RUUID


def _create_simple_queue(
    identifier: str, resource: simple_queue.simple_queue_model
) -> bool:
    attributes = {}

    if resource.fifo:
        attributes.update({"FifoQueue": str(resource.fifo)})

    rv = raw_aws_client.run_client_function(
        "sqs",
        "create_queue",
        {"QueueName": resource.queue_name, "Attributes": attributes},
    )

    print_deployment_step("CREATE", f"Created queue {resource.name}")

    output_info = {
        "queue_name": resource.queue_name,
        "cdev_name": resource.name,
        "ruuid": RUUID,
        "queue_url": rv.get("QueueUrl"),
    }

    # rv does not contain the arn of the queue so we need a second call

    rv = raw_aws_client.run_client_function(
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

    cdev_cloud_mapper.add_identifier(identifier),
    cdev_cloud_mapper.update_output_value(identifier, output_info)
    return True


def _update_simple_queue(
    previous_resource: simple_queue.simple_queue_model,
    new_resource: simple_queue.simple_queue_model,
) -> bool:
    _remove_simple_queue(previous_resource.hash, previous_resource)
    _create_simple_queue(new_resource.hash, new_resource)
    return True


def _remove_simple_queue(
    identifier: str, resource: simple_queue.simple_queue_model
) -> bool:
    queue_url = cdev_cloud_mapper.get_output_value_by_hash(identifier, "queue_url")

    raw_aws_client.run_client_function("sqs", "delete_queue", {"QueueUrl": queue_url})

    print_deployment_step("DELETE", f"Removed queue {resource.name}")

    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")
    return True


def handle_simple_queue_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_queue(
                resource_diff.new_resource.hash, resource_diff.new_resource
            )
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            return _update_simple_queue(
                resource_diff.previous_resource, resource_diff.new_resource
            )
        elif resource_diff.action_type == Action_Type.DELETE:
            return _remove_simple_queue(
                resource_diff.previous_resource.hash, resource_diff.previous_resource
            )

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
