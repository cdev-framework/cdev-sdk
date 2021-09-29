import json
import os
from typing import Dict

from pydantic.types import NonPositiveInt

from cdev.utils import project

from ..models import Rendered_State

from ..models import CloudMapping

from cdev.settings import SETTINGS as cdev_settings

from ..utils import environment as cdev_environment
from ..utils.logger import get_cdev_logger
from ..utils.paths import get_full_path_from_internal_folder
log = get_cdev_logger(__name__)

_info = {}


def _set_resource_info() -> Dict:
    if project.check_if_project_exists():
        current_environment_name = cdev_environment.get_current_environment()
        current_environment_info = cdev_environment.get_environment_info(current_environment_name)

        _info['FULL_CLOUD_MAPPING_PATH'] = get_full_path_from_internal_folder(current_environment_info.cloud_mapping_fp)
        _info['FULL_RESOURCE_STATE_PATH'] = get_full_path_from_internal_folder(current_environment_info.resource_state_fp)

    else:
        raise Exception

def get_resource_state_path():
    _set_resource_info()
    return _info.get("FULL_RESOURCE_STATE_PATH")


def write_resource_state(state: Rendered_State):
    _set_resource_info()
    with open(_info.get("FULL_RESOURCE_STATE_PATH"), 'w') as fp:
        fp.write(state.json(indent=4))


def write_cloud_mapping(state: CloudMapping):
    _set_resource_info()
    with open(_info.get("FULL_CLOUD_MAPPING_PATH"), 'w') as fp:
        fp.write(state.json(indent=4))



def load_resource_state() -> Rendered_State:
    _set_resource_info()
    log.debug(_info.get("FULL_RESOURCE_STATE_PATH"))
    if not os.path.isfile(_info.get("FULL_RESOURCE_STATE_PATH")):
        # TODO Throw error
        return None


    with open(_info.get("FULL_RESOURCE_STATE_PATH")) as fp:
        previous_data = json.load(fp)

    try: 
        rv = Rendered_State(**previous_data)
        return rv
    except BaseException as e:
        print(e)
        return None


def load_cloud_mapping() -> CloudMapping:
    _set_resource_info()
    if not os.path.isfile(_info.get("FULL_CLOUD_MAPPING_PATH")):
        # TODO Throw error
        return None

    with open(_info.get("FULL_CLOUD_MAPPING_PATH")) as fp:
        previous_data = json.load(fp)

    try: 
        rv = CloudMapping(**previous_data)
        return rv
    except BaseException as e:
        print(e)
        return None


def get_resource(original_resource_name: str, original_resource_type: str):
    resource_state = load_resource_state()
    for component in resource_state.rendered_components:
        for resource in component.rendered_resources:
            if not resource.ruuid == original_resource_type:
                continue

            if not resource.name == original_resource_name:
                continue

            return resource

    raise Exception