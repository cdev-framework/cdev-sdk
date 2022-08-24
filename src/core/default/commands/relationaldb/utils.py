from typing import Tuple

from core.constructs.workspace import Workspace
from core.default.resources.simple.relational_db import simple_relational_db_model

RUUID = "cdev::simple::relationaldb"


def get_db_info_from_cdev_name(
    component_name: str, cdev_database_name: str
) -> Tuple[str, str, str]:
    """_summary_

    Args:
        component_name (str): Name of the component that the resource is in
        cdev_database_name (str): Name of the resource

    Returns:
        Tuple[str,str,str]: cluster_arn, secret_arn, db_name
    """

    ws = Workspace.instance()

    cluster_arn = ws.get_backend().get_cloud_output_value_by_name(
        ws.get_resource_state_uuid(),
        component_name,
        RUUID,
        cdev_database_name,
        "cluster_arn",
    )

    secret_arn = ws.get_backend().get_cloud_output_value_by_name(
        ws.get_resource_state_uuid(),
        component_name,
        RUUID,
        cdev_database_name,
        "secret_arn",
    )

    db_resource_model: simple_relational_db_model = (
        ws.get_backend().get_resource_by_name(
            ws.get_resource_state_uuid(),
            component_name,
            RUUID,
            cdev_database_name,
        )
    )

    return (cluster_arn, secret_arn, db_resource_model.DatabaseName)
