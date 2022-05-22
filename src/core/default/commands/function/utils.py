from typing import Tuple, Optional

from core.constructs.workspace import Workspace


RUUID = "cdev::simple::function"


def get_cloud_id_from_cdev_name(component_name: str, cdev_function_name: str) -> Optional[str]:
    try:
        ws = Workspace.instance()

        cloud_id = ws.get_backend().get_cloud_output_value_by_name(
            ws.get_resource_state_uuid(),
            component_name,
            RUUID,
            cdev_function_name,
            "cloud_id",
        )

        return cloud_id
    except Exception as e:
        print(f"Could not find cloud id")
        print(e)
    return None
