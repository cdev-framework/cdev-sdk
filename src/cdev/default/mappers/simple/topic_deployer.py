from enum import Enum
from types import new_class
from typing import Dict, List

from botocore.endpoint import Endpoint

from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import hasher, logger
from cdev.resources.simple import topic as simple_topic
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from ..aws import aws_client as raw_aws_client
from cdev.output import print_deployment_step

log = logger.get_cdev_logger(__name__)
RUUID = simple_topic.RUUID


def _create_simple_topic(identifier: str, resource: simple_topic.simple_topic_model) -> bool:
    attributes = {}

    if resource.fifo:
        attributes.update({
            "FifoTopic": str(resource.fifo)
        })

    
    rv = raw_aws_client.run_client_function("sns", "create_topic", {
        "Name": resource.topic_name,
        "Attributes": attributes
    })
    print_deployment_step("CREATE", f"Created topic {resource.name}")

    output_info = {
        "topic_name": resource.topic_name,
        "cdev_name": resource.name,
        "ruuid": RUUID,
        "arn": rv.get("TopicArn"),
        "cloud_id": rv.get("TopicArn")
    }

    cdev_cloud_mapper.add_identifier(identifier),
    cdev_cloud_mapper.update_output_value(identifier, output_info)
    return True


def _update_simple_topic(previous_resource: simple_topic.simple_topic_model, new_resource: simple_topic.simple_topic_model) -> bool:
    _remove_simple_topic(previous_resource.hash, previous_resource)
    _create_simple_topic(new_resource.hash, new_resource)
    return True


def _remove_simple_topic(identifier: str, resource: simple_topic.simple_topic_model) -> bool:
    topic_arn = cdev_cloud_mapper.get_output_value_by_hash(identifier, "arn")
    
    raw_aws_client.run_client_function("sns", "delete_topic", {
        "TopicArn": topic_arn
    })

    print_deployment_step("DELETE", f"Removed topic {resource.name}")
    
    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")
    return True



def handle_simple_topic_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_topic(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            return _update_simple_topic(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            return _remove_simple_topic(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


def add_subscriber(topic_arn: str, protocol: str, endpoint: str) -> str:
    rv = raw_aws_client.run_client_function("sns", "subscribe", {
        "TopicArn": topic_arn, 
        "Protocol": protocol,
        "Endpoint": endpoint,
        "ReturnSubscriptionArn": True
    })

    return rv.get("SubscriptionArn")


def remove_subscriber(subscription_arn: str):
    rv = raw_aws_client.run_client_function("sns", "unsubscribe", {
        "SubscriptionArn": subscription_arn
    })
