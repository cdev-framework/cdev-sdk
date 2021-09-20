import json
import os
from typing import List, Dict


from pydantic import BaseModel
from pydantic.types import FilePath

from cdev.settings import SETTINGS as cdev_settings
from cdev.models import CloudMapping, CloudState, Rendered_State

from . import hasher as cdev_hasher

from .logger import get_cdev_logger

log = get_cdev_logger(__name__)


CDEV_ENVIRONMENT_INFO_FILE = cdev_settings.get("CDEV_ENVIRONMENT_INFO_FILE")
PROJECT_BASE_LOCATION = cdev_settings.get("INTERNAL_FOLDER_NAME")

class cdev_environment(BaseModel):
    name: str
    resource_state_fp: str
    cloud_mapping_fp: str
    settings: Dict


class environment_info(BaseModel):
    environments: List[cdev_environment]
    current_environment: str




def create_environment(environment_name: str) -> bool:
    current_environment = get_environment_info_object()

    if environment_name in set([x.name for x in current_environment.environments]):
        log.error(f"Environment {environment_name} already exists")
        raise Exception

    STATE_DIR = os.path.dirname(CDEV_ENVIRONMENT_INFO_FILE)
    
    RESOURCE_STATE_PATH_FULL = os.path.join(STATE_DIR, f"{environment_name}_resource_state.json")
    CLOUD_MAPPING_PATH_FULL = os.path.join(STATE_DIR, f"{environment_name}_cloud_mapping.json")
    
    RESOURCE_STATE_PATH = os.path.relpath(os.path.join(STATE_DIR, f"{environment_name}_resource_state.json"), PROJECT_BASE_LOCATION)
    CLOUD_MAPPING_PATH = os.path.relpath( os.path.join(STATE_DIR, f"{environment_name}_cloud_mapping.json"),  PROJECT_BASE_LOCATION)


    _create_resource_state(RESOURCE_STATE_PATH_FULL)
    _create_cloud_mapping(CLOUD_MAPPING_PATH_FULL)

    current_environment.environments.append(cdev_environment(**{
        "name": environment_name,
        "resource_state_fp": RESOURCE_STATE_PATH,
        "cloud_mapping_fp": CLOUD_MAPPING_PATH,
        "settings": []
    }))

    _initialize_backend_files(RESOURCE_STATE_PATH_FULL, CLOUD_MAPPING_PATH_FULL)

    _write_environment_info_object(current_environment)

    return True


def get_environment_info_object() -> environment_info:
    if not os.path.isfile(CDEV_ENVIRONMENT_INFO_FILE): 
        return None

    if os.stat(CDEV_ENVIRONMENT_INFO_FILE).st_size == 0:
        return environment_info(**{
            "environments": [],
            "current_environment": ""
        })

    with open(CDEV_ENVIRONMENT_INFO_FILE) as fh:
        environment_info_json = json.load(fh)


    return environment_info(**environment_info_json)


def get_environment_info(environment_name: str) -> cdev_environment:
    environment_info = get_environment_info_object()

    if not environment_info:
        return None

    environments_by_name = {x.name:x for x in environment_info.environments}

    if not environment_name in environments_by_name:
        raise Exception

    return environments_by_name.get(environment_name)


def get_all_environment_names() -> List[str]:
    environment_info = get_environment_info_object()

    return [x.name for x in environment_info.environments]


def set_current_environment(environment_name: str) -> bool:
    environment_info = get_environment_info_object()

    current_environments = set([x.name for x in environment_info.environments])

    if not environment_name in current_environments:
        raise Exception

    environment_info.current_environment = environment_name

    _write_environment_info_object(environment_info)


def get_current_environment() -> str:
    environment_info = get_environment_info_object()

    if not environment_info:
        return None

    return environment_info.current_environment


def get_current_environment_hash()-> str:
    return cdev_hasher.hash_string(get_current_environment())


############################################
##### HELPER FUNCTIONS
############################################

def _write_environment_info_object(new_environment_info: environment_info) -> bool:
    with open(CDEV_ENVIRONMENT_INFO_FILE, 'w') as fh:
        fh.write(new_environment_info.json(indent=4))

    return True


def _create_resource_state(fp):
    _touch(fp)

def _create_cloud_mapping(fp):
    _touch(fp)


def _touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def _initialize_backend_files(resource_state_fp: FilePath, cloud_mapping_fp: FilePath):
    # NO previous local state so write an empty object to the file then return the object
    project_state = Rendered_State(**{
        "rendered_components": None,
        "hash": "0"
    })

    cloudmapping = CloudMapping(**{
        "state": {
            "0": CloudState(**{
                "output": {},
                "deployed_resources": []
            })
        }
    })

    with open(resource_state_fp, "w") as fh:
        fh.write(project_state.json(indent=4))

    with open(cloud_mapping_fp, "w") as fh:
        fh.write(cloudmapping.json(indent=4))
