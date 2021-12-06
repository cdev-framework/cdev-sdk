import os
from typing import List, Dict

from pydantic import BaseModel
from pydantic.types import DirectoryPath

from .backend import Backend_Configuration

WORKSPACE_INFO_FILENAME = "workspace_info.json"
WORKSPACE_INFO_DIR = ".cdev"


class Workspace_Info(BaseModel):
    backend_configuration: Backend_Configuration
    configuration: Dict

    def __init__(__pydantic_self__, backend_configuration: Backend_Configuration, configuration: Dict) -> None:
        """
        Represents the data needed to create a new cdev workspace:
        
        Parameters:
            backend_configuration: configuration information about the backend for this workspaces
            configuration: variable overrides to use for the workspace settings. 
            
        """
        
        super().__init__(**{
            "backend_configuration": backend_configuration,
            "configuration": configuration
        })



def create_new_workspace(workspace_info: Workspace_Info, base_dir: DirectoryPath):
    """
    Create a new workspace based on the information provided. 

    Args:
        workspace_info (Workspace_Info): information about the backend configuration

    Raises:
        WorkSpaceAlreadyCreated  
    """
    base_cdev_dir = os.path.join(base_dir, WORKSPACE_INFO_DIR)
    if not os.path.isdir(base_cdev_dir):
        os.mkdir(base_cdev_dir)


    with open(os.path.join(base_cdev_dir, WORKSPACE_INFO_FILENAME), 'w') as fh:
        fh.write(workspace_info.json(indent=4))



def check_if_workspace_exists(base_dir: DirectoryPath) -> bool:
    return os.path.isfile(os.path.join(base_dir, WORKSPACE_INFO_DIR, WORKSPACE_INFO_FILENAME))

