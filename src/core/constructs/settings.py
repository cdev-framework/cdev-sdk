"""
Basic available settings
"""
import os

from typing import Optional, List

from pydantic import BaseModel, BaseSettings, ValidationError

from core.utils.module_loader import (
    import_class,
    import_module,
    ImportClassError,
    ImportModuleError,
)


from dataclasses import dataclass, field
from core.utils.exceptions import cdev_core_error


###############################
##### Exceptions
###############################


@dataclass
class SettingsError(cdev_core_error):
    help_message: str = ""
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class LoadSettingsClassError(SettingsError):
    help_message: str = """
    Consider fixing the provided error, or change your base settings class using the following command:
    cdev environment settings_information --key base_class --new-value <settings-module>
    """
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class InitializeSettingsClassError(SettingsError):
    help_message: str = """
    Consider fixing the provided error, or change your base settings class using the following command:
    cdev environment settings_information --key base_class --new-value <settings-module>
    """
    help_resources: List[str] = field(default_factory=lambda: [])


###############################
##### Classes
###############################


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

    # Cache Directory
    CACHE_DIRECTORY: str = os.path.join(INTERMEDIATE_FOLDER_LOCATION, "cache")

    # Bucket to use as a place to store resource artifacts in the cloud
    S3_ARTIFACTS_BUCKET: Optional[str] = None

    # AWS account information
    AWS_REGION: str = "us-east-1"

    # Base entry point file for the workspace
    ENTRY_POINT_FILE: str = os.path.join(BASE_PATH, "cdev_project.py")

    DEPLOYMENT_PLATFORM: str = "x86"

    USE_DOCKER: bool = False

    class Config:
        env_prefix = "cdev_"
        validate_assignment = True
        # extra = 'allow'


###############################
##### Api
###############################


def initialize_settings(info: Settings_Info) -> Settings:
    """Initialize the Settings object from a given Setting Info

    Args:
        info (Settings_Info)

    Returns:
        Settings
    """
    class_name = info.base_class.split(".")[-1]
    module_name = ".".join(info.base_class.split(".")[:-1])

    try:
        base_settings_class = import_class(module_name, class_name)
    except ImportClassError as e:
        raise LoadSettingsClassError(
            error_message=f"""When loading '{class_name}' from '{module_name}' as the settings base class the following exception occurred:
            {e.error_message}
            """
        )
    except ImportModuleError as e:
        raise LoadSettingsClassError(
            error_message=f"""When loading '{module_name}' to load the base settings class ('{class_name}') the following exception occurred:
            {e.error_message}
            """
        )

    kw_args = {}

    if info.secret_dir:
        kw_args["_secrets_dir"] = info.secret_dir

    # All the settings are stored as relative paths so they need to convert to full paths
    t = {k: os.path.join(os.getcwd(), v) for k, v in kw_args.items()}

    try:
        base_setting_obj = base_settings_class(**t)
    except ValidationError as e:
        raise InitializeSettingsClassError(
            error_message=f"""Could not Initialize Settings class '{info.base_class}' because of a data validation error ->

            {e}
            """
        )
    except Exception as e:
        raise InitializeSettingsClassError(error_message=f"{e}")

    if info.user_setting_module:
        for settings_module in info.user_setting_module:

            try:
                module = import_module(settings_module)
            except ImportModuleError as e:
                raise InitializeSettingsClassError(
                    error_message=f"""Error when loading '{settings_module}' as a Settings initialize module for '{info.base_class}':
                    {e.error_message}
                    """
                )

            for setting in dir(module):
                if setting.isupper():
                    setting_value = getattr(module, setting)

                    try:
                        setattr(base_setting_obj, setting, setting_value)
                    except ValidationError as e:
                        raise InitializeSettingsClassError(
                            error_message=f"""Error setting property '{setting}' as [green]{setting_value}[/green] from initialization module '{settings_module}' for base class '{info.base_class}' ->

                            {e}
                            """
                        )
                    except Exception as e:
                        raise InitializeSettingsClassError(error_message=f"{e}")

    return base_setting_obj
