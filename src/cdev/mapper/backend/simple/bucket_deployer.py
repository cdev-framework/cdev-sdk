from enum import Enum
from types import new_class
from typing import Dict, List

from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import hasher, logger
from cdev.resources.simple import object_store as simple_object_store
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from cdev.output import print_deployment_step
from ..aws import aws_client as raw_aws_client

log = logger.get_cdev_logger(__name__)
RUUID = "cdev::simple::bucket"

class event_hander_types(Enum):
    SQS = "sqs"
    LAMBDA = "lambda"
    SNS = "sns"


def _create_simple_bucket(identifier: str, resource: simple_object_store.simple_bucket_model) -> bool:
    # TODO create buckets in different region
    raw_aws_client.run_client_function("s3", "create_bucket", {
        "Bucket": resource.bucket_name
    })
    
    print_deployment_step("CREATE", f"Created bucket {resource.name}")
    
    output_info = {
        "bucket_name": resource.bucket_name,
        "cloud_id": f"arn:aws:s3:::{resource.bucket_name}",
        "arn": f"arn:aws:s3:::{resource.bucket_name}",
        "cdev_name": resource.name,
        "ruuid": RUUID
    }

    cdev_cloud_mapper.add_identifier(identifier),
    cdev_cloud_mapper.update_output_value(identifier, output_info)

    return True

def _update_simple_bucket(previous_resource: simple_object_store.simple_bucket_model, new_resource: simple_object_store.simple_bucket_model) -> bool:
    _remove_simple_bucket(previous_resource.hash, previous_resource)
    _create_simple_bucket(new_resource.hash, new_resource)

    return True


def _remove_simple_bucket(identifier: str, resource: simple_object_store.simple_bucket_model) -> bool:
    raw_aws_client.run_client_function("s3", "delete_bucket", {
        "Bucket": resource.bucket_name
    })

    print_deployment_step("DELETE", f"Removed bucket {resource.name}")

    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")
    return True



def handle_simple_bucket_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_bucket(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            return _update_simple_bucket(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            return _remove_simple_bucket(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")


def add_eventsource(bucket_name: str, handler_type: event_hander_types, handler_arn: str, events: List[str]) -> str:
    # Per https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_notification_configuration
    # The only available function for adding event handlers to a bucket is 'put_bucket_notification_configuration", but this function takes 
    # in a whole configuration and completely overwrites to the new one. Therefor, we need to get the current configuration and then add this
    # new event handler and write it back to preserve previous eventsources. 
    
    current_events = _get_current_bucket_event_configuration(bucket_name)

    if not current_events:
        current_events = {}
    

    log.debug(f"CURRENT BUCKET EVENTS {current_events}")

    event_id = hasher.hash_list([handler_type.value, handler_arn, hasher.hash_list(events)])
    base_config = {
        'Events': events,
        'Id': event_id
    }

    if handler_type == event_hander_types.LAMBDA:
        base_config.update({
            'LambdaFunctionArn': handler_arn
        })

        current_lambda_handlers =  current_events.get("LambdaFunctionConfigurations")

        if not current_lambda_handlers:
            current_lambda_handlers = []

        current_lambda_handlers.append(base_config)
        current_events["LambdaFunctionConfigurations"] = current_lambda_handlers
    elif handler_type == event_hander_types.SNS:
        base_config.update({
            'TopicArn': handler_arn
        })

        current_sns_handlers =  current_events.get("TopicConfigurations")

        if not current_sns_handlers:
            current_sns_handlers = []

        current_sns_handlers.append(base_config)
        current_events["TopicConfigurations"] = current_sns_handlers
    elif handler_type == event_hander_types.SQS:
        base_config.update({
            'QueueArn': handler_arn
        })

        current_sqs_handlers =  current_events.get("QueueConfigurations")

        if not current_sqs_handlers:
            current_sqs_handlers = []
        
        current_sqs_handlers.append(base_config)
        current_events["QueueConfigurations"] = current_sqs_handlers
    else:
        raise Exception

    _write_bucket_event_configuration(bucket_name, current_events)

    return event_id


def remove_eventsource(bucket_name: str, bucket_event_id: str) -> bool:
    current_events = _get_current_bucket_event_configuration(bucket_name)

    if not current_events:
        raise Exception
    
    log.debug(f"CURRENT BUCKET EVENTS {current_events}")

    keys = ["TopicConfigurations", "QueueConfigurations", "LambdaFunctionConfigurations"]

    found_val = False
    for key in keys:
        if found_val:
            break

        if not current_events.get(key):
            continue

        for val in current_events.get(key):
            if val.get("Id") == bucket_event_id:
                log.debug(f"Found event in bucket event {key} {val}; {bucket_event_id}")
                remove_val = val
                remove_key = key
                found_val = True
                break


    if not found_val:
        raise Exception

    current_events.get(remove_key).remove(remove_val)

    log.debug(f"New configuration after removal {current_events}")
    _write_bucket_event_configuration(bucket_name, current_events)

    return True

def _get_current_bucket_event_configuration(bucket_name: str) -> Dict:
    aws_rv = raw_aws_client.run_client_function("s3", "get_bucket_notification_configuration", {
        "Bucket": bucket_name
    })

    rv = {
        "TopicConfigurations": aws_rv.get("TopicConfigurations"),
        "QueueConfigurations": aws_rv.get("QueueConfigurations"),
        "LambdaFunctionConfigurations": aws_rv.get("LambdaFunctionConfigurations"),
    }

    return rv


def _write_bucket_event_configuration(bucket_name: str, new_config: Dict) -> bool:
    final_config = {k:v for k,v in new_config.items() if v}


    raw_aws_client.run_client_function("s3", "put_bucket_notification_configuration", {
        "Bucket": bucket_name,
        "NotificationConfiguration": final_config
    })

    return True
