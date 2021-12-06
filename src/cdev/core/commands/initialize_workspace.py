import os


from cdev.core.constructs import workspace as cdev_workspace
from cdev.core.constructs.backend import Local_Backend_Configuration

def initialize_workspace(args):
    base_project_dir = os.getcwd()

    if cdev_workspace.check_if_workspace_exists(base_project_dir):
        print("Workspace already initialized")

    workspace_info = cdev_workspace.Workspace_Info(
        Local_Backend_Configuration({"name": "Daniel"}), 
        {"CDEV_VAR": 1}
    )

    cdev_workspace.create_new_workspace(workspace_info, base_project_dir)

    return

