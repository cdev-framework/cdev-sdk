from typing import Dict, List

from core.constructs.resource import ResourceModel
from core.constructs.workspace import Workspace

RUUID = "cdev::simple::table"

def get_cloud_output_from_cdev_name(component_name: str, cdev_name: str) -> str:
    try:
        ws = Workspace.instance()


        cloud_output = ws.get_backend().get_cloud_output_by_name(
            ws.get_resource_state_uuid(),
            component_name,
            RUUID, 
            cdev_name
        )

        return cloud_output
    except Exception as e:
        print(f"Could not find resource {component_name}:{RUUID}:{cdev_name}")
        print(e)
        return None



def get_resource_from_cdev_name(component_name: str, cdev_name: str) -> ResourceModel:
    try:
        ws = Workspace.instance()


        resource = ws.get_backend().get_resource_by_name(
            ws.get_resource_state_uuid(),
            component_name,
            RUUID, 
            cdev_name
        )

        return resource
    except Exception as e:
        print(f"Could not find resource {component_name}:{RUUID}:{cdev_name}")
        print(e)
        return None




_attribute_types_to_python_type = {"S": [str], "N": [int, float], "B": [bytes]}


def validate_data(data: Dict, attributes: Dict, keys: List[Dict]) -> bool:
    for key in keys:
        if not key.get("attribute_name") in data:
            return (False, f"Table key {key.get('attribute_name')} not in data")

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

    return (True, "")


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
