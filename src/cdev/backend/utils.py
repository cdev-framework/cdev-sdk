import json
import os

from pydantic.types import NonPositiveInt

from cdev.frontend.models import Rendered_State

from cdev.settings import SETTINGS as cdev_settings


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



def load_local_state() -> Rendered_State:
    # TODO Make this a class and json representation use json schema 
    if not os.path.isfile(FULL_LOCAL_STATE_PATH):
        # TODO Throw error
        return None


    with open(FULL_LOCAL_STATE_PATH) as fp:
        previous_data = json.load(fp)

    try: 
        rv = Remote_State(**previous_data)
        return rv
    except BaseException as e:
        print(e)
        return None
