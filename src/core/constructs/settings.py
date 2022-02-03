"""
Basic available settings 
"""

import os

from typing import Any, Optional
from rich.logging import RichHandler

from rich.traceback import install

from typing import Set

from pydantic import (
    BaseModel,
    BaseSettings,
)

from core.utils.module_loader import import_class

# install(show_locals=False)

SETTINGS = {}


SETTINGS["OUTPUT_PLAIN"] = False
SETTINGS["SHOW_LOGS"] = True

SETTINGS["CONSOLE_LOG_LEVEL"] = "ERROR"
SETTINGS["CAPTURE_OUTPUT"] = False


SETTINGS["PULL_INCOMPATIBLE_LIBRARIES"] = True

SETTINGS["DEPLOYMENT_PLATFORM"] = "arm64"
SETTINGS["DEPLOYMENT_PYTHON_VERSION"] = "py38"


SETTINGS["LOGGING_INFO"] = {
    "version": 1,
    "formatters": {
        "jsonFormatter": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
        "simpleFormatter": {
            "format": "%(asctime)s %(name)s - %(levelname)s: %(message)s"
        },
        "richFormatter": {"format": "%(name)s - %(message)s"},
    },
    "handlers": {
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "jsonFormatter",
            "filename": ".cdev/logs/userlogs",
        },
        "simpleHandler": {
            "class": "logging.StreamHandler",
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "formatter": "simpleFormatter",
        },
        "richHandler": {
            "class": "rich.logging.RichHandler",
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "formatter": "richFormatter",
            "markup": True,
            "show_path": False,
            "show_time": False,
            "rich_tracebacks": True,
        },
    },
    "loggers": {
        "cli": {"level": "DEBUG", "handlers": ["fileHandler"], "propagate": False},
        "commands": {"level": "DEBUG", "handlers": ["fileHandler"], "propagate": False},
        "frontend": {"level": "DEBUG", "handlers": ["fileHandler"], "propagate": False},
        "backend": {"level": "DEBUG", "handlers": ["fileHandler"], "propagate": False},
        "mapper": {"level": "DEBUG", "handlers": ["fileHandler"], "propagate": False},
        "resources": {
            "level": "DEBUG",
            "handlers": ["fileHandler"],
            "propagate": False,
        },
        "utils": {"level": "DEBUG", "handlers": ["fileHandler"], "propagate": False},
        "cli_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False,
        },
        "commands_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False,
        },
        "frontend_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False,
        },
        "backend_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False,
        },
        "mapper_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False,
        },
        "resources_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False,
        },
        "utils_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False,
        },
        "cli_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False,
        },
        "commands_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False,
        },
        "frontend_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False,
        },
        "backend_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False,
        },
        "mapper_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False,
        },
        "resources_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False,
        },
        "utils_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False,
        },
    },
    "root": {"level": "ERROR", "handlers": ["simpleHandler"]},
    "disable_existing_loggers": False,
}





class Settings_Info(BaseModel):
    base_class: str
    env_file: Optional[str]
    user_setting_module: Optional[str]
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
    S3_ARTIFACTS_BUCKET = "cdev-demo-project-artifacts"

    # AWS account information
    AWS_REGION = "us-east-1"
    
    # Base entry point file for the workspace
    ENTRY_POINT_FILE = os.path.join(
        BASE_PATH, "cdev_project.py"
    )

    DEPLOYMENT_PLATFORM = "x86"

    class Config:
        env_prefix = 'CDEV_' 
        arbitrary_types_allowed = True



def initialize_settings(info: Settings_Info) -> Settings:
    class_name = info.base_class.split('.')[-1]
    module_name = ".".join(info.base_class.split('.')[:-1])

    base_settings_class = import_class(module_name, class_name)

    kw_args = {}

    if info.secret_dir:
        kw_args['_secrets_dir'] = info.secret_dir

    if info.env_file:
        kw_args['_env_file'] = info.env_file

    base_setting_obj = base_settings_class(**kw_args)

    return base_setting_obj

    


