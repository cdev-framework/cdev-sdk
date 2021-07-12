import json
import os

from pydantic.types import NonPositiveInt

from ..models import Rendered_State

from .models import CloudMapping

from cdev.settings import SETTINGS as cdev_settings





BASE_PATH = cdev_settings.get("BASE_PATH")

STATE_FOLDER_LOCATION = cdev_settings.get("STATE_FOLDER") 
RESOURCE_STATE_LOCATION = cdev_settings.get("RESOURCE_STATE_LOCATION")
CLOUD_MAPPING_LOCATION = cdev_settings.get("CLOUD_MAPPING_LOCATION")

FULL_RESOURCE_STATE_PATH = os.path.join(BASE_PATH, RESOURCE_STATE_LOCATION)
FULL_CLOUD_MAPPING_PATH = os.path.join(BASE_PATH, CLOUD_MAPPING_LOCATION)


def get_resource_state_path():
    return FULL_RESOURCE_STATE_PATH


def write_resource_state(state: Rendered_State):
    with open(FULL_RESOURCE_STATE_PATH, 'w') as fp:
        fp.write(state.json(indent=4))


def write_cloud_mapping(state: CloudMapping):
    print("WRITE")
    with open(FULL_CLOUD_MAPPING_PATH, 'w') as fp:
        fp.write(state.json(indent=4))



def load_resource_state() -> Rendered_State:
    if not os.path.isfile(FULL_RESOURCE_STATE_PATH):
        # TODO Throw error
        return None


    with open(FULL_RESOURCE_STATE_PATH) as fp:
        previous_data = json.load(fp)

    try: 
        rv = Rendered_State(**previous_data)
        return rv
    except BaseException as e:
        print(e)
        return None


def load_cloud_mapping() -> CloudMapping:
    if not os.path.isfile(FULL_CLOUD_MAPPING_PATH):
        # TODO Throw error
        return None

    with open(FULL_CLOUD_MAPPING_PATH) as fp:
        previous_data = json.load(fp)

    try: 
        rv = CloudMapping(**previous_data)
        return rv
    except BaseException as e:
        print(e)
        return None
