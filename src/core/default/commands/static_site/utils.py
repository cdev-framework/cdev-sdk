from typing import Optional, Dict

from core.constructs.resource import ResourceModel
from core.constructs.workspace import Workspace

RUUID = "cdev::simple::staticsite"


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
