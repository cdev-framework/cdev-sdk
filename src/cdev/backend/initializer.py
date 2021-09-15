import os

from ..models import CloudMapping, CloudState

from . import utils as backend_utils
from ..models import Rendered_State




def is_backend_initialized() -> bool:
    # NO previous local state so write an empty object to the file then return the object
    path_of_backend = backend_utils.get_resource_state_path()

    if not os.path.isfile(path_of_backend):
        return False

    return True
