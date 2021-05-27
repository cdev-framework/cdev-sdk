import json
import os

from jsonschema import validate

from cdev.settings import SETTINGS as cdev_settings
from cdev.schema import utils as schema_utils

BASE_PATH = cdev_settings.get("BASE_PATH")

STATE_FOLDER_LOCATION = cdev_settings.get("STATE_FOLDER") 
LOCAL_STATE_LOCATION = cdev_settings.get("LOCAL_STATE_LOCATION")

FULL_LOCAL_STATE_PATH = os.path.join(BASE_PATH, LOCAL_STATE_LOCATION)

def update_local_state(project_info):
    print(project_info)
    previous_local_state = _load_local_state()
    print(previous_local_state)
    


def _load_local_state():
    # TODO Make this a class and json representation use json schema 
    if not os.path.isfile(FULL_LOCAL_STATE_PATH):
        # TODO Throw error
        return None


    with open(FULL_LOCAL_STATE_PATH) as fp:
        rv = json.load(fp)

    for function_state in rv.get("functions"):
        function_schema = schema_utils.get_schema("FUNCTION")
        validate(function_state, function_state)

    return rv