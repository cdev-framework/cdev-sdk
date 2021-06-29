import os

from . import utils as backend_utils

def initialize_backend(project_name):
    # NO previous local state so write an empty object to the file then return the object
    project_state = {
        "components": {
        },
        "project_name": project_name
    }

    backend_utils.write_local_state(project_state)

    return project_state


def is_backend_initialized() -> bool:
    # NO previous local state so write an empty object to the file then return the object
    path_of_backend = backend_utils.get_local_state_path()

    if not os.path.isfile(path_of_backend):
        return False

    return True