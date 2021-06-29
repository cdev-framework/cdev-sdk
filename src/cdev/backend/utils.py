import json
import os

from cdev.settings import SETTINGS as cdev_settings
from cdev.schema import utils as schema_utils


BASE_PATH = cdev_settings.get("BASE_PATH")

STATE_FOLDER_LOCATION = cdev_settings.get("STATE_FOLDER") 
LOCAL_STATE_LOCATION = cdev_settings.get("LOCAL_STATE_LOCATION")

FULL_LOCAL_STATE_PATH = os.path.join(BASE_PATH, LOCAL_STATE_LOCATION)


def get_local_state_path():
    return FULL_LOCAL_STATE_PATH

def write_local_state(state):
    for component_name in state.get("components"):
        try:
            state.get("components").get(component_name).pop('hash_to_function')

        except Exception as e:
            print(f"ERROR -> {e}")
            
    
    with open(FULL_LOCAL_STATE_PATH, 'w') as fp:
        json.dump(state, fp, indent=4)

def load_local_state():
    # TODO Make this a class and json representation use json schema 
    if not os.path.isfile(FULL_LOCAL_STATE_PATH):
        # TODO Throw error
        return None


    with open(FULL_LOCAL_STATE_PATH) as fp:
        previous_data = json.load(fp)

    rv = {}

    for component_name in previous_data.get("components"):

        previous_data.get("components").get(component_name)['hash_to_function'] = {}
        
    
        for function_state in previous_data.get("components").get(component_name).get("functions"):
            schema_utils.validate(schema_utils.SCHEMA.FRONTEND_FUNCTION, function_state)

            total_hash = function_state.get("hash")

            previous_data.get("components").get(component_name)['hash_to_function'][total_hash] = function_state

    
    return previous_data
