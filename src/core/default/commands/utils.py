from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from core.constructs.resource import ResourceModel
from core.constructs.workspace import Workspace
from core.utils.exceptions import cdev_core_error


###############################
##### Exceptions
###############################


@dataclass
class ResourceNameError(cdev_core_error):
    help_message: str = (
        "   Resource should be identified by <comp_name>.<resource_name>"
    )
    help_resources: List[str] = field(default_factory=lambda: [])


###############################
##### API
###############################


def get_cloud_output_from_cdev_name(
    component_name: str, ruuid: str, cdev_name: str
) -> Dict:
    ws = Workspace.instance()

    cloud_output = ws.get_backend().get_cloud_output_by_name(
        ws.get_resource_state_uuid(), component_name, ruuid, cdev_name
    )

    return cloud_output


def get_resource_from_cdev_name(
    component_name: str, ruuid: str, cdev_name: str
) -> ResourceModel:
    ws = Workspace.instance()

    resource = ws.get_backend().get_resource_by_name(
        ws.get_resource_state_uuid(), component_name, ruuid, cdev_name
    )

    return resource


def get_component_and_resource_from_qualified_name(full_name: str) -> Tuple[str, str]:
    component_and_function = full_name.split(".")

    if len(component_and_function) != 2:
        raise ResourceNameError(
            error_message=f"'{full_name}' is not properly structured as resource identifier"
        )

    component_name = component_and_function[0]
    resource_name = component_and_function[1]

    return component_name, resource_name
