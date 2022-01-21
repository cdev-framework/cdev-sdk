from enum import Enum
from types import new_class
from typing import Any, Dict, List

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.resources.simple import object_store as simple_object_store
from core.output.output_manager import OutputTask
from core.utils import hasher


from .. import aws_client as raw_aws_client


RUUID = "cdev::simple::bucket"


class event_hander_types(Enum):
    SQS = "sqs"
    LAMBDA = "lambda"
    SNS = "sns"


def _create_simple_bucket(
    transaction_token: str, 
    namespace_token: str, 
    resource:  simple_object_store.simple_bucket_model,
    output_task: OutputTask
) -> Dict:


    cloud_bucket_name = f"{resource.bucket_name}-{namespace_token}"

    output_task.update(advance=1, comment=f'Creating Bucket {cloud_bucket_name}')
    
    # TODO create buckets in different region
    rv = raw_aws_client.run_client_function(
        "s3", "create_bucket", {"Bucket": cloud_bucket_name}
    )

    output_task.update(advance=1, comment=f'Created Bucket {cloud_bucket_name}')

    output_info = {
        "bucket_name": cloud_bucket_name,
        "cloud_id": f"arn:aws:s3:::{cloud_bucket_name}",
        "arn": f"arn:aws:s3:::{cloud_bucket_name}",
    }


    return output_info


def _update_simple_bucket(
    transaction_token: str, 
    namespace_token: str,
    previous_resource: simple_object_store.simple_bucket_model,
    new_resource: simple_object_store.simple_bucket_model,
    previous_output: Dict,
    output_task: OutputTask
) -> Dict:

    _remove_simple_bucket(transaction_token,  previous_output, output_task)
    new_info =  _create_simple_bucket(transaction_token, namespace_token, new_resource, output_task)

    return new_info


def _remove_simple_bucket(
    transaction_token: str,  previous_output: Dict, output_task: OutputTask
):

    previous_bucket_name = previous_output.get('bucket_name')

    output_task.update(advance=1, comment=f'Deleting Bucket {previous_bucket_name}')

    raw_aws_client.run_client_function(
        "s3", "delete_bucket", {"Bucket": previous_bucket_name}
    )

    output_task.update(advance=1, comment=f'Deleted Bucket {previous_bucket_name}')


def add_eventsource(
    bucket_name: str,
    handler_type: event_hander_types,
    handler_arn: str,
    events: List[str],
) -> str:
    # Per https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_notification_configuration
    # The only available function for adding event handlers to a bucket is 'put_bucket_notification_configuration", but this function takes
    # in a whole configuration and completely overwrites to the new one. Therefor, we need to get the current configuration and then add this
    # new event handler and write it back to preserve previous eventsources.

    current_events = _get_current_bucket_event_configuration(bucket_name)

    if not current_events:
        current_events = {}


    event_id = hasher.hash_list(
        [handler_type.value, handler_arn, hasher.hash_list(events)]
    )
    base_config = {"Events": events, "Id": event_id}

    if handler_type == event_hander_types.LAMBDA:
        base_config.update({"LambdaFunctionArn": handler_arn})

        current_lambda_handlers = current_events.get("LambdaFunctionConfigurations")

        if not current_lambda_handlers:
            current_lambda_handlers = []

        current_lambda_handlers.append(base_config)
        current_events["LambdaFunctionConfigurations"] = current_lambda_handlers
    elif handler_type == event_hander_types.SNS:
        base_config.update({"TopicArn": handler_arn})

        current_sns_handlers = current_events.get("TopicConfigurations")

        if not current_sns_handlers:
            current_sns_handlers = []

        current_sns_handlers.append(base_config)
        current_events["TopicConfigurations"] = current_sns_handlers
    elif handler_type == event_hander_types.SQS:
        base_config.update({"QueueArn": handler_arn})

        current_sqs_handlers = current_events.get("QueueConfigurations")

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


    keys = [
        "TopicConfigurations",
        "QueueConfigurations",
        "LambdaFunctionConfigurations",
    ]

    found_val = False
    for key in keys:
        if found_val:
            break

        if not current_events.get(key):
            continue

        for val in current_events.get(key):
            if val.get("Id") == bucket_event_id:
                remove_val = val
                remove_key = key
                found_val = True
                break

    if not found_val:
        raise Exception

    current_events.get(remove_key).remove(remove_val)

    _write_bucket_event_configuration(bucket_name, current_events)

    return True


def _get_current_bucket_event_configuration(bucket_name: str) -> Dict:
    aws_rv = raw_aws_client.run_client_function(
        "s3", "get_bucket_notification_configuration", {"Bucket": bucket_name}
    )

    rv = {
        "TopicConfigurations": aws_rv.get("TopicConfigurations"),
        "QueueConfigurations": aws_rv.get("QueueConfigurations"),
        "LambdaFunctionConfigurations": aws_rv.get("LambdaFunctionConfigurations"),
    }

    return rv


def _write_bucket_event_configuration(bucket_name: str, new_config: Dict) -> bool:
    final_config = {k: v for k, v in new_config.items() if v}

    raw_aws_client.run_client_function(
        "s3",
        "put_bucket_notification_configuration",
        {"Bucket": bucket_name, "NotificationConfiguration": final_config},
    )

    return True



def handle_simple_bucket_deployment( 
        transaction_token: str, 
        namespace_token: str, 
        resource_diff: Resource_Difference, 
        previous_output: Dict[simple_object_store.simple_bucket_output, Any],
        output_task: OutputTask
    ) -> Dict:
    try:
        if resource_diff.action_type == Resource_Change_Type.CREATE:
            return _create_simple_bucket(
                transaction_token,
                namespace_token,
                resource_diff.new_resource,
                output_task
            )
            
        elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
            return _update_simple_bucket(
                transaction_token,
                namespace_token,
                simple_object_store.simple_bucket_model(resource_diff.previous_resource.dict()),
                resource_diff.new_resource,
                previous_output,
                output_task
            )

        elif resource_diff.action_type == Resource_Change_Type.DELETE:
            _remove_simple_bucket(
               transaction_token,
               previous_output,
               output_task
            )

            return {}

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")