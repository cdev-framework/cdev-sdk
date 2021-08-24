"""
Basic available settings 
"""

import os
import sys
import logging
from rich.logging import RichHandler

SETTINGS = {
    
}

SETTINGS["BASE_PATH"] = os.path.abspath(os.getcwd())
SETTINGS["INTERNAL_FOLDER_NAME"] = os.path.join(SETTINGS.get("BASE_PATH"), ".cdev")

SETTINGS["CDEV_INTERMEDIATE_FOLDER_LOCATION"] = os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME"), "intermediate")
SETTINGS["CDEV_INTERMEDIATE_FILES_LOCATION"] = os.path.join(SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "functions")

SETTINGS["STATE_FOLDER"] = os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME"), "state")
SETTINGS["RESOURCE_STATE_LOCATION"] = os.path.join(SETTINGS.get("STATE_FOLDER"), "resourcestate.json")
SETTINGS["CLOUD_MAPPING_LOCATION"] = os.path.join(SETTINGS.get("STATE_FOLDER"), "cloudmapping.json")

SETTINGS["CDEV_PROJECT_FILE"] = os.path.join(SETTINGS.get("BASE_PATH"), "cdev_project.py")
SETTINGS["COMPONENT_FILE_NAME"] = "cdev_component.py"

SETTINGS["S3_ARTIFACTS_BUCKET"] = "cdev-demo-project-artificats"

SETTINGS["OUTPUT_PLAIN"] = False
SETTINGS["SHOW_LOGS"] = True


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
            "level": "DEBUG",
            "formatter": "simpleFormatter",
        },
        "richHandler": {
            "class": "rich.logging.RichHandler",
            "level": "DEBUG",
            "formatter": "richFormatter",
            "markup": True,
            "show_path": False,
            "show_time": False
        }
    },
    "loggers":{
        "cli": {
            "level": "ERROR",
            "handlers": ["fileHandler"]
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
            "level": "ERROR",
            "handlers": ["richHandler"]
        },
        "frontend_rich": {
            "level": "DEBUG",
            "handlers": ["richHandler"],
            "propagate": False
        },
        "backend_rich": {
            "level": "DEBUG",
            "handlers": ["richHandler"],
            "propagate": False
        },
        "mapper_rich": {
            "level": "DEBUG",
            "handlers": ["richHandler"],
            "propagate": False
        },
        "resources_rich": {
            "level": "DEBUG",
            "handlers": ["richHandler"],
            "propagate": False
        },
        "utils_simple": {
            "level": "DEBUG",
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "cli_simple": {
            "level": "ERROR",
            "handlers": ["simpleHandler"]
        },
        "frontend_simple": {
            "level": "DEBUG",
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "backend_simple": {
            "level": "DEBUG",
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "mapper_simple": {
            "level": "DEBUG",
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "resources_simple": {
            "level": "DEBUG",
            "handlers": ["simpleHandler"],
            "propagate": False
        },
        "utils_simple": {
            "level": "DEBUG",
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
