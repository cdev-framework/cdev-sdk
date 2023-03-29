import json
from typing import Any, Dict
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.default.resources.simple import kinesis
from core.constructs.output_manager import OutputTask
from core.utils import hasher

from .. import aws_client


def _create_simple_data_stream(
    transaction_token: str,
    namespace_token: str,
    resource: kinesis.data_stream_model,
    output_task: OutputTask,
) -> Dict:

    full_namespace_suffix = hasher.hash_list([namespace_token, str(uuid4())])

    data_stream_name = f"cdev-data-stream-{full_namespace_suffix}"

    output_task.update(comment=f"Creating Data Stream {data_stream_name}")

    if resource.stream_mode == kinesis.StreamMode.ON_DEMAND:
        attributes = {
            "StreamName": data_stream_name,
            "StreamModeDetails": {"StreamMode": "ON_DEMAND"},
        }
    else:
        attributes = {
            "StreamName": data_stream_name,
            "ShardCount": resource.shard_count,
            "StreamModeDetails": {"StreamMode": "PROVISIONED"},
        }

    aws_client.run_client_function(
        "kinesis",
        "create_stream",
        attributes,
    )

    output_info = {
        "data_stream_name": data_stream_name,
        "cdev_name": resource.name,
    }

    # rv does not contain the arn of the queue so we need a second call

    rv = aws_client.run_client_function(
        "kinesis",
        "describe_stream_summary",
        {"StreamName": data_stream_name},
    )

    output_info.update(
        {
            "cloud_id": rv.get("StreamDescriptionSummary").get("StreamARN"),
            "arn": rv.get("StreamDescriptionSummary").get("StreamARN"),
        }
    )

    return output_info


def _update_simple_queue(
    transaction_token: str,
    namespace_token: str,
    previous_resource: kinesis.data_stream_model,
    new_resource: kinesis.data_stream_model,
    previous_output: Dict,
    output_task: OutputTask,
) -> Dict:
    _remove_simple_data_stream(transaction_token, previous_output, output_task)
    new_info = _create_simple_data_stream(
        transaction_token, namespace_token, new_resource, output_task
    )
    return new_info


def _remove_simple_data_stream(
    transaction_token: str, previous_output: Dict, output_task: OutputTask
) -> None:
    stream_arn = previous_output.get("arn")

    output_task.update(comment="Deleting Stream")

    aws_client.run_client_function(
        "kinesis", "delete_stream", {"StreamARN": stream_arn}
    )


def handle_simple_data_stream_deployment(
    transaction_token: str,
    namespace_token: str,
    resource_diff: Resource_Difference,
    previous_output: Dict[str, Any],
    output_task: OutputTask,
) -> Dict:
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        return _create_simple_data_stream(
            transaction_token, namespace_token, resource_diff.new_resource, output_task
        )

    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
        return _update_simple_queue(
            transaction_token,
            namespace_token,
            kinesis.data_stream_model(**resource_diff.previous_resource.dict()),
            resource_diff.new_resource,
            previous_output,
            output_task,
        )

    elif resource_diff.action_type == Resource_Change_Type.DELETE:
        _remove_simple_data_stream(transaction_token, previous_output, output_task)

        return {}
