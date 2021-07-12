import os

from .models import CloudMapping

from . import utils as backend_utils
from ..models import Rendered_State

def initialize_backend(project_name):
    # NO previous local state so write an empty object to the file then return the object
    project_state = Rendered_State(**{
        "rendered_components": None,
        "hash": "1"
    })

    cloudmapping = CloudMapping(**{
        "state": {
            "1": [{}]
        }
    })

    backend_utils.write_resource_state(project_state)
    backend_utils.write_cloud_mapping(cloudmapping)

    return project_state


def is_backend_initialized() -> bool:
    # NO previous local state so write an empty object to the file then return the object
    path_of_backend = backend_utils.get_local_state_path()

    if not os.path.isfile(path_of_backend):
        return False

    return True
