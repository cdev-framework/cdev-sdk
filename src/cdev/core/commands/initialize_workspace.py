from cdev.core.constructs.workspace import Workspace
from pydantic.types import DirectoryPath, FilePath
from cdev.core.settings import SETTINGS as cdev_settings

WORKSPACE_INFO_DIR = cdev_settings.get("ROOT_FOLDER_NAME")
WORKSPACE_INFO_FILENAME = cdev_settings.get("WORKSPACE_FILE_NAME")


def initialize_workspace_cli(args):
    
    backend_config = args.backend_configuration if args.backend_configuration else "HELLO WORLD"

    initialize_workspace(backend_config)


def initialize_workspace(backend_configuration: str):
    Workspace(backend_configuration)