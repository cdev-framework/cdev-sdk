from cdev.core.constructs.backend import Backend_Configuration
from cdev.core.constructs.workspace import Workspace
from pydantic.types import DirectoryPath, FilePath
from cdev.core.settings import SETTINGS as cdev_settings

WORKSPACE_INFO_DIR = cdev_settings.get("ROOT_FOLDER_NAME")
WORKSPACE_INFO_FILENAME = cdev_settings.get("WORKSPACE_FILE_NAME")


def initialize_workspace_cli(args):
    
    backend_config = args.backend_configuration if args.backend_configuration else {}

    try:
        initialize_workspace(backend_config)
    except Exception as e:
        raise(e)

def initialize_workspace(backend_configuration: Backend_Configuration, workspace_class: str=None):
    
    if not workspace_class:
        try:
            Workspace().initialize_workspace(backend_configuration)
        except Exception as e:
            raise(e)

    else:
        # Dynamically load python class for the workspace
        pass