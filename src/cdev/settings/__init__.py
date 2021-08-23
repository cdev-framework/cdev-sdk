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



SETTINGS["LOGGING_INFO"] = {
    "version": 1,
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        },
        "simpleFormatter": {
            "format": "%(asctime)s %(name)s - %(levelname)s: %(message)s"
        }
    },
    "handlers" : {
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": ".cdev/logs/userlogs",
        },
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simpleFormatter",
        },
        "richHandler": {
            "class": "rich.logging.RichHandler",
            "level": "DEBUG",
            "formatter": "simpleFormatter"
        }
    },
    "loggers":{
        "cli": {
            "level": "ERROR",
            "handlers": ["fileHandler"]
        },
        "frontend": {
            "level": "DEBUG",
            "handlers": ["fileHandler", "richHandler"],
            "propagate": False
        }
    }, 
    "root": {
        "level": "ERROR",
        "handlers": ["consoleHandler"]
    },
    "disable_existing_loggers": False

}
