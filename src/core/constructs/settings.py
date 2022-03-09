"""
Basic available settings 
"""
import os

from typing import Any, Optional
from rich.logging import RichHandler

from rich.traceback import install

from typing import List, Set

from pydantic import (
    BaseModel,
    BaseSettings,
)

from core.utils.module_loader import import_class, import_module


class Settings_Info(BaseModel):
    base_class: str
    user_setting_module: Optional[List[str]]
    secret_dir: Optional[str]
    

class Settings(BaseSettings):

    # Starting Path for workspace
    BASE_PATH: str = os.path.abspath(os.getcwd())


    INTERNAL_FOLDER_NAME: str = ".cdev"

    # Configuration file for a workspace
    WORKSPACE_FILE: str = "workspace_info.json"


    INTERMEDIATE_FOLDER_LOCATION: str = os.path.join(
        BASE_PATH, INTERNAL_FOLDER_NAME, "intermediate"
    )

    # Bucket to use as a place to store resource artifacts in the cloud
    S3_ARTIFACTS_BUCKET: str = "cdev-demo-project-artifacts"

    # AWS account information
    AWS_REGION: str = "us-east-1"
    
    # Base entry point file for the workspace
    ENTRY_POINT_FILE: str = os.path.join(
        BASE_PATH, "cdev_project.py"
    )

    DEPLOYMENT_PLATFORM: str = "x86"

    USE_DOCKER: bool = False


    class Config:
        env_prefix = 'cdev_'
        validate_assignment = True
        #extra = 'allow'



def initialize_settings(info: Settings_Info) -> Settings:
    class_name = info.base_class.split('.')[-1]
    module_name = ".".join(info.base_class.split('.')[:-1])

    base_settings_class = import_class(module_name, class_name)

    kw_args = {}

    if info.secret_dir:
        kw_args['_secrets_dir'] = info.secret_dir


    # All the settings are stored as relative paths so they need to convert to full paths
    t = {k:os.path.join(os.getcwd(),v) for k,v in kw_args.items()}
    
    base_setting_obj = base_settings_class(**t)

    if info.user_setting_module:
        for settings_module in info.user_setting_module:
            

            module = import_module(settings_module)

            for setting in dir(module):
                if setting.isupper():
                    setting_value = getattr(module, setting)

                    setattr(base_setting_obj, setting, setting_value)

       

    return base_setting_obj

    


