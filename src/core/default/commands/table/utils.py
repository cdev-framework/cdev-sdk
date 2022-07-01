from typing import Dict, List, Tuple, Any, Optional

from core.constructs.resource import ResourceModel

from core.constructs.workspace import Workspace
import boto3

RUUID = "cdev::simple::table"


def get_cloud_output_from_cdev_name(component_name: str, cdev_name: str) -> Optional[Dict]:
    try:
        ws = Workspace.instance()

        cloud_output = ws.get_backend().get_cloud_output_by_name(
            ws.get_resource_state_uuid(), component_name, RUUID, cdev_name
        )

        return cloud_output
    except Exception as e:
        print(f"Could not find resource {component_name}:{RUUID}:{cdev_name}")
        print(e)
        return None


def get_resource_from_cdev_name(component_name: str, cdev_name: str) -> Optional[ResourceModel]:
    try:
        ws = Workspace.instance()

        resource = ws.get_backend().get_resource_by_name(
            ws.get_resource_state_uuid(), component_name, RUUID, cdev_name
        )

        return resource
    except Exception as e:
        print(f"Could not find resource {component_name}:{RUUID}:{cdev_name}")
        print(e)
        return None


_attribute_types_to_python_type = {"S": [str], "N": [int, float], "B": [bytes]}


def validate_data(data: Dict, attributes: Dict, keys: List[Dict]) -> Tuple[bool, str]:
    for key in keys:
        if not key.get("attribute_name") in data:
            return False, f"Table key {key.get('attribute_name')} not in data"

        valid_types = _attribute_types_to_python_type.get(
            attributes.get(key.get("attribute_name"))
        )

        is_val_valid_type = False
        for attribute_type in valid_types:
            if isinstance(data.get(key.get("attribute_name")), attribute_type):
                is_val_valid_type = True
                break

        if not is_val_valid_type:
            return (
                False,
                f"Table key {key.get('attribute_name')} ({valid_types}) not correct type in data ({type(data.get(key.get('attribute_name')))})",
            )

    return True, ""


def recursive_translate_data(value) -> Dict:
    if isinstance(value, str):
        transformed_val = {"S": value}
    elif isinstance(value, (int, float)):
        transformed_val = {"N": value}
    elif isinstance(value, float):
        transformed_val = {"N": value}
    elif isinstance(value, bytes):
        transformed_val = {"B": value}
    elif isinstance(value, bool):
        transformed_val = {"BOOl": value}
    elif not value:
        transformed_val = {"NULL": True}
    elif isinstance(value, list):
        if all(isinstance(x, str) for x in value):
            transformed_val = {"SS": [x for x in value]}
        elif all(isinstance(x, (int, float)) for x in value):
            transformed_val = {"NS": [x for x in value]}
        elif all(isinstance(x, bytes) for x in value):
            transformed_val = {"BS": [x for x in value]}
        else:
            transformed_val = {"L": [recursive_translate_data(value)]}

    elif isinstance(value, dict):
        transformed_val = {k: recursive_translate_data(v) for k, v in value.items()}

    else:
        raise Exception

    return transformed_val

def get_dynamodb_info_from_cdev_name(
    component_name: str, cdev_database_name: str
) -> Tuple[Any, Any]:
    """_summary_

    Args:
        component_name (str): Name of the component that the resource is in
        cdev_database_name (str): Name of the resource

    Returns:
        Tuple[str,str,str]: cluster_arn, secret_arn, db_name
    """
    try:
        ws = Workspace.instance()
        cloud_arn = ws.get_backend().get_cloud_output_value_by_name(
            ws.get_resource_state_uuid(),
            component_name,
            RUUID,
            cdev_database_name,
            "cloud_id",
        )
        table_name = cloud_arn[cloud_arn.find(":table/") + 7 : len(cloud_arn)]
        return [cloud_arn, table_name]
    except Exception as e:
        print(e)


def dynamodb_item_action(operation_type: str, table_name: str, item: dict) -> None:
    rendered_client = boto3.client("dynamodb")
    try:
        if operation_type == "put_item":
            rendered_client.put_item(TableName=table_name, Item=item)
        elif operation_type == "delete_item":
            rendered_client.delete_item(TableName=table_name, Key=item)
        elif operation_type == "get_item":
            res = rendered_client.get_item(TableName=table_name, Key=item)
            print(res)
        else:
            res = "Invalid operation type"
            print(res)
    except Exception as e:
        raise e
