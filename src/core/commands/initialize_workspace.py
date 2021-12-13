import os
from pydantic.types import DirectoryPath, FilePath

from ..constructs.backend import Backend_Configuration
from ..constructs.workspace import Workspace, Workspace_Info, load_workspace_configuration

from ..settings import SETTINGS as cdev_settings

WORKSPACE_INFO_DIR = cdev_settings.get("ROOT_FOLDER_NAME")
WORKSPACE_INFO_FILENAME = cdev_settings.get("WORKSPACE_FILE_NAME")


def initialize_workspace_cli(args):
    print(f"Initialize workspace cli args {args}")

    workspace_config = load_workspace_configuration(os.getcwd())
    
    try:
        _initialize_workspace(workspace_config)
    except Exception as e:
        raise(e)



def _initialize_workspace(workspace_config: Workspace_Info):
    print("here")
    try:
        Workspace.instance().initialize_workspace(workspace_config)
    except Exception as e:
        raise e

