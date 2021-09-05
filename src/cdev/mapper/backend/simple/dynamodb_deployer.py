from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import table as simple_dynamodb_table
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from ..aws import aws_client as raw_aws_client

log = logger.get_cdev_logger(__name__)


def _create_simple_dynamodb_table(identifier: str, resource: simple_dynamodb_table.simple_table_model) -> bool:

    # Create Table
    rv = raw_aws_client.run_client_function("dynamodb", "create_table", {
            "TableName": resource.table_name,
            "AttributeDefinitions": resource.attributes,
            "KeySchema": resource.keys,
            "BillingMode": "PAY_PER_REQUEST"
        }, wait={
            "name": "table_exists",
            "args": {
                "TableName": resource.table_name
            }
        }
    )

    output_info = {
        "table_name": resource.table_name,
        "cloud_id": rv.get("TableDescription").get("TableArn"), 
        "cdev_name": resource.name,
        "ruuid": "cdev::simple::table"
    }

    cdev_cloud_mapper.add_identifier(identifier),
    cdev_cloud_mapper.update_output_value(identifier, output_info)


    return True


def _update_simple_dynamodb_table(previous_resource: simple_dynamodb_table.simple_table_model, new_resource: simple_dynamodb_table.simple_table_model) -> bool:
    if not previous_resource.table_name == new_resource.table_name:
        log.error("CAN NOT CHANGE TABLE NAME")
        return False

    if not previous_resource.keys == new_resource.keys:
        log.error("CANNOT CHANGE PRIMARY KEYS OF TABLE")
        return False

    if not previous_resource.attributes == new_resource.attributes:
        log.error("CANNOT CHANGE ATTRIBUTES OF TABLE")
        return False

    return False


def _remove_simple_dynamodb_table(identifier: str, resource: simple_dynamodb_table.simple_table_model) -> bool:
    
    table_name = cdev_cloud_mapper.get_output_value(identifier, "table_name")

    raw_aws_client.run_client_function("dynamodb", "delete_table", {
        "TableName": table_name,
        
    }, wait={
            "name": "table_not_exists",
            "args": {
                "TableName": resource.table_name
            }
    })

    return True


def handle_simple_table_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_dynamodb_table(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:

            return _update_simple_dynamodb_table(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            
            return _remove_simple_dynamodb_table(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
