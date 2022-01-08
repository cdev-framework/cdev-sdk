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
        "core.default.workspace",
        "local_workspace",
        {
            "backend_configuration": {
                "python_module": "core.default.backend",
                "python_class": "LocalBackend",
                "config": {
                    "base_folder": base_project_dir,
                    "central_state_file": "centralstate.json",
                },
            },
            "initialization_file": "cdev_project",
        },
    )

    manager.create_new_workspace(workspace_info)

    return
