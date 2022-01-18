import json
from pydantic import FilePath
import os
import shutil
from typing import Dict
from types import MappingProxyType

from core.constructs.resource_state import Resource_State  
from .types import FrozenDict

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, frozenset):
            return list(obj)

        if isinstance(obj, FrozenDict):
            return dict(obj)

        return json.JSONEncoder.default(self, obj)


def safe_json_write(obj: Dict, fp: FilePath):
    """
    Safely write files by first writing to a tmp file then copying to final location. This ensures that no file is
    partially written thus leaving a file in an unrecoverable place.

    Arguments:
        obj (Dict): The dictionary that should be written
        fp (FilePath): The path the file should be written at

    """

    tmp_fp = f"{fp}.tmp"

    if os.path.isfile(tmp_fp):
        os.remove(tmp_fp)

    try:
        with open(tmp_fp, "w") as fh:
            json.dump(obj, fh, indent=4, cls=CustomEncoder)

    except Exception as e:
        print(e)
        raise e

    try:
        shutil.copyfile(tmp_fp, fp)
    except Exception as e:
        raise e

    os.remove(tmp_fp)



def load_resource_state(fp: FilePath) -> Resource_State:
    with open(fp, "r") as fh:
        _mutable_json = json.load(fh)

    _mutable_json['components'] = _recursive_make_immutable(_mutable_json.get('components'))

    return Resource_State(**_mutable_json)
    
def _recursive_make_immutable(o):
    if isinstance(o, list):
        return frozenset([_recursive_make_immutable(x) for x in o])
    elif isinstance(o, dict):
        return FrozenDict({k: _recursive_make_immutable(v) for k, v in o.items()})
    return o

    