import os

from ..constructs import workspace as cdev_workspace
from ..constructs.backend import Backend_Configuration

def create_workspace(args):
    base_project_dir = os.getcwd()

    if cdev_workspace.check_if_workspace_exists(base_project_dir):
        print("Workspace already initialized")

    workspace_info = cdev_workspace.Workspace_Info(
        Backend_Configuration({"name": "Daniel"}), 
        
    )

    cdev_workspace.create_new_workspace(workspace_info, base_project_dir)

    return

