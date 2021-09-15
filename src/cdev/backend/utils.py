import json
import os

from pydantic.types import NonPositiveInt

from ..models import Rendered_State

from ..models import CloudMapping

from cdev.settings import SETTINGS as cdev_settings

from ..utils import environment as cdev_environment
from ..utils.logger import get_cdev_logger
from ..utils.paths import get_full_path_from_internal_folder
log = get_cdev_logger(__name__)

current_environment_name = cdev_environment.get_current_environment()
current_environment_info = cdev_environment.get_environment_info(current_environment_name)


FULL_CLOUD_MAPPING_PATH = get_full_path_from_internal_folder(current_environment_info.cloud_mapping_fp)
FULL_RESOURCE_STATE_PATH = get_full_path_from_internal_folder(current_environment_info.resource_state_fp)

def get_resource_state_path():
    return FULL_RESOURCE_STATE_PATH


def write_resource_state(state: Rendered_State):
    with open(FULL_RESOURCE_STATE_PATH, 'w') as fp:
        fp.write(state.json(indent=4))


def write_cloud_mapping(state: CloudMapping):
    with open(FULL_CLOUD_MAPPING_PATH, 'w') as fp:
        fp.write(state.json(indent=4))



def load_resource_state() -> Rendered_State:
    log.debug(FULL_RESOURCE_STATE_PATH)
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
