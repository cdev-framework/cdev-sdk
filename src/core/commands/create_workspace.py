import os

from ..constructs import workspace as cdev_workspace
from ..constructs.backend import Backend_Configuration

from ..default.workspace import local_workspace_manager


def create_workspace(args):
    base_project_dir = os.getcwd()
    manager = local_workspace_manager(base_project_dir)

    if manager.check_if_workspace_exists():
        print("Workspace already initialized")

    workspace_info = cdev_workspace.Workspace_Info(
        "cdev.default.backend",
        "Local_Backend",
        {
            
        }
    )

    manager.create_new_workspace(workspace_info)

    return

