from typing import Tuple, Any

from core.constructs.workspace import Workspace

RUUID = "cdev::simple::table"


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
