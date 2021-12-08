import os
from pydantic.types import DirectoryPath, FilePath

from cdev.core.constructs.backend import Backend_Configuration
from cdev.core.constructs.workspace import Workspace, Workspace_Info, load_workspace_configuration

from cdev.core.settings import SETTINGS as cdev_settings

WORKSPACE_INFO_DIR = cdev_settings.get("ROOT_FOLDER_NAME")
WORKSPACE_INFO_FILENAME = cdev_settings.get("WORKSPACE_FILE_NAME")


def initialize_workspace_cli(args):
    print(args)

    workspace_config = args.workspace_config if args.workspace_config else load_workspace_configuration(os.getcwd())
    
    try:
        _initialize_workspace(workspace_config)
    except Exception as e:
        raise(e)



def _initialize_workspace(workspace_config: Workspace_Info, workspace_class: str=None):
    print("here")
    try:
        Workspace.instance().initialize_workspace(workspace_config)
    except Exception as e:
        raise e

