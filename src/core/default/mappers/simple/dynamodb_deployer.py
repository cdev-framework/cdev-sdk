from typing import Any, Dict, Optional
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.constructs.output_manager import OutputTask
from core.default.resources.simple import table
from core.utils import hasher

from .. import aws_client


def _create_simple_dynamodb_table(
    transaction_token: str,
    namespace_token: str,
    resource: table.simple_table_model,
    output_task: OutputTask,
) -> Dict:
    full_namespace_suffix = hasher.hash_list([namespace_token, str(uuid4())])
    table_name = f"cdev-table-{full_namespace_suffix}"
    output_task.update(
        comment="[blink]Creating Table. This will take a few seconds.[/blink]"
    )
    key_schema = [
        {"AttributeName": x.attribute_name, "KeyType": x.key_type.value}
        for x in resource.keys
    ]
    secondary_key_schema = [
        {
            "IndexName": x.index_name,
            "KeySchema": [{"AttributeName": x.attribute_name, "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }
        for x in resource.secondary_key
    ]
    key_schema.sort(key=lambda x: x.get("KeyType"))
    create_dict = {
        "TableName": table_name,
        "AttributeDefinitions": [
            {
                "AttributeName": x.attribute_name,
                "AttributeType": x.attribute_type.value,
            }
            for x in resource.attributes
        ],
        "KeySchema": key_schema,
        "BillingMode": "PAY_PER_REQUEST",
    }
    if len(secondary_key_schema) > 0:
        create_dict["GlobalSecondaryIndexes"] = secondary_key_schema

    rv = aws_client.run_client_function(
        "dynamodb",
        "create_table",
        create_dict,
        wait={"name": "table_exists", "args": {"TableName": table_name}},
    )
    output_info = {
        "table_name": table_name,
        "cloud_id": rv.get("TableDescription").get("TableArn"),
        "arn": rv.get("TableDescription").get("TableArn"),
        "cdev_name": resource.name,
        "ruuid": resource.ruuid,
    }
    return output_info


def _update_simple_dynamodb_table(
    transaction_token: str,
    namespace_token: str,
    previous_resource: table.simple_table_model,
    new_resource: table.simple_table_model,
    previous_output: Dict,
    output_task: OutputTask,
) -> Dict:
    raise Exception


def _remove_simple_dynamodb_table(
    transaction_token: str, previous_output: Dict, output_task: OutputTask
) -> None:
    table_name = previous_output.get("table_name")

    output_task.update(
        comment="[blink]Deleting Table. This will take a few seconds.[/blink]"
    )

    aws_client.run_client_function(
        "dynamodb",
        "delete_table",
        {
            "TableName": table_name,
        },
        wait={"name": "table_not_exists", "args": {"TableName": table_name}},
    )


def handle_simple_table_deployment(
    transaction_token: str,
    namespace_token: str,
    resource_diff: Resource_Difference,
    previous_output: Dict[str, Any],
    output_task: OutputTask,
) -> Optional[Dict]:
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        return _create_simple_dynamodb_table(
            transaction_token, namespace_token, resource_diff.new_resource, output_task
        )
    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
        return _update_simple_dynamodb_table(
            transaction_token,
            namespace_token,
            table.simple_table_model(**resource_diff.previous_resource.dict()),
            resource_diff.new_resource,
            previous_output,
            output_task,
        )
    elif resource_diff.action_type == Resource_Change_Type.DELETE:
        _remove_simple_dynamodb_table(transaction_token, previous_output, output_task)
        return {}
