"""
Basic available settings 
"""

import os
import sys
import logging
from rich.logging import RichHandler

from rich.traceback import install
#install(show_locals=False)   

SETTINGS = {
    
}

SETTINGS["BASE_PATH"] = os.path.abspath(os.getcwd())
SETTINGS["INTERNAL_FOLDER_NAME"] = os.path.join(SETTINGS.get("BASE_PATH"), ".cdev")

SETTINGS["CDEV_INTERMEDIATE_FOLDER_LOCATION"] = os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME"), "intermediate")
SETTINGS["CDEV_INTERMEDIATE_FILES_LOCATION"] = os.path.join(SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "functions")

SETTINGS["STATE_FOLDER"] = os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME"), "state")
SETTINGS["CDEV_ENVIRONMENT_INFO_FILE"] = os.path.join(SETTINGS.get("STATE_FOLDER"), "environment_info.json")
SETTINGS["CLOUD_MAPPING_LOCATION"] = os.path.join(SETTINGS.get("STATE_FOLDER"), "cloudmapping.json")

SETTINGS["CDEV_PROJECT_FILE"] = os.path.join(SETTINGS.get("BASE_PATH"), "cdev_project.py")
SETTINGS["COMPONENT_FILE_NAME"] = "cdev_component.py"

SETTINGS["S3_ARTIFACTS_BUCKET"] = "cdev-demo-project-artificats"


SETTINGS["AWS_REGION"] = "us-east-1"
SETTINGS["AWS_ACCOUNT"] = "369004794337"


SETTINGS["OUTPUT_PLAIN"] = False
SETTINGS["SHOW_LOGS"] = True

SETTINGS["CONSOLE_LOG_LEVEL"] = "ERROR"



SETTINGS["LOGGING_INFO"] = {
    "version": 1,
    "formatters": {
        "jsonFormatter": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        },
        "simpleFormatter": {
            "format": "%(asctime)s %(name)s - %(levelname)s: %(message)s"
        },
        "richFormatter": {
            "format": "%(name)s - %(message)s"
        }
    },
    "handlers" : {
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
            "rich_tracebacks": True
        }
    },
    "loggers":{
        "cli": {
            "level": "DEBUG",
            "handlers": ["fileHandler"],
            "propagate": False
        },
        "commands": {
            "level": "DEBUG",
            "handlers": ["fileHandler"],
            "propagate": False
        },
        "frontend": {
            "level": "DEBUG",
            "handlers": ["fileHandler"],
            "propagate": False
        },
        "backend": {
            "level": "DEBUG",
            "handlers": ["fileHandler"],
            "propagate": False
        },
        "mapper": {
            "level": "DEBUG",
            "handlers": ["fileHandler"],
            "propagate": False
        },
        "resources": {
            "level": "DEBUG",
            "handlers": ["fileHandler"],
            "propagate": False
        },
        "utils": {
            "level": "DEBUG",
            "handlers": ["fileHandler"],
            "propagate": False
        },
        "cli_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False
        },
        "commands_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False
        },
        "frontend_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False
        },
        "backend_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False
        },
        "mapper_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False
        },
        "resources_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["richHandler"],
            "propagate": False
        },
        "utils_rich": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "cli_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "commands_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "frontend_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "backend_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "mapper_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "resources_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "utils_simple": {
            "level": SETTINGS["CONSOLE_LOG_LEVEL"],
            "handlers": ["simpleHandler"],
            "propagate": False
        },
    }, 
    "root": {
        "level": "ERROR",
        "handlers": ["simpleHandler"]
    },
    "disable_existing_loggers": False

}
