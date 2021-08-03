

import time
import re
from typing import Dict
import botocore
import json

from cdev.resources.aws.dynamodb import DynamoDBTable, DynamoDBTable_Output
from cdev.models import Resource_State_Difference, Action_Type
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper

from .aws_client import run_client_function, get_boto_client, monitor_status

client = get_boto_client("dynamodb")


def create_table(identifier: str,resource: DynamoDBTable) -> bool:
    rv = _create_table(resource)
    if rv:
        cdev_cloud_mapper.add_cloud_resource(identifier, resource)
        cdev_cloud_mapper.update_output_value(identifier, rv)


def delete_table(identifier: str,resource: DynamoDBTable) -> bool:
    _delete_table(resource)

    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)


def _create_table(resource: DynamoDBTable) -> Dict[DynamoDBTable_Output, str]:
    try:
        #response = client.create_table(
        #    AttributeDefinitions=[x.dict() for x in resource.AttributeDefinitions],
        #    TableName=resource.TableName,
        #    KeySchema=[x.dict() for x in resource.KeySchema],
        #    ProvisionedThroughput={
        #        'ReadCapacityUnits': 5,
        #        'WriteCapacityUnits': 5
        #    }
        #)
        args = {
                "AttributeDefinitions": [x.dict() for x in resource.AttributeDefinitions],
                "TableName": resource.TableName,
                "KeySchema": [x.dict() for x in resource.KeySchema],
                "ProvisionedThroughput": {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
            }
        }
        wait = {
            "name": "table_exists",
            "args": {
                "TableName": resource.TableName
            }
        }
        response = run_client_function("dynamodb", "create_table", args, wait)
        print(f"AWS RESPONSE -> {response}")
        
        return {
                    DynamoDBTable_Output.TableName: resource.TableName,
                    DynamoDBTable_Output.TableArn: "123"
        }

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None


def _delete_table(resource: DynamoDBTable) -> bool:
    try:
        wait = {
            "name": "table_not_exists",
            "args": {
                "TableName": resource.TableName
            }
        }
        response = run_client_function("dynamodb", "delete_table", {"TableName": resource.TableName}, wait)

        return response

    except botocore.exceptions.ClientError as e:
        print(e.response)
        return None
        

def handle_dynamodb_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            create_table(resource_diff.new_resource.hash, resource_diff.new_resource)
            return True
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            print("NOT SUPPORTED DYNAMODB UPDATES")
            return False
        elif resource_diff.action_type == Action_Type.DELETE:
            delete_table(resource_diff.previous_resource.hash, resource_diff.previous_resource)
            return True

    except Exception as e:
        print(e)
        return False
