import json
from pydantic import FilePath
import os
import shutil
from typing import Dict, List
from types import MappingProxyType

from core.constructs.resource_state import Resource_State  
from ..constructs.models import frozendict

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, frozenset):
            return list(obj)

        if isinstance(obj, frozendict):
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

    for component in _mutable_json['components']:
        # The actual resource and reference models need to be immutable data structures so that they can have a 
        # __hash__ value.
        component['resources'] = [_recursive_make_immutable(x) for x in component.get('resources')]
        component['references'] = [_recursive_make_immutable(x) for x in component.get('references')]
        if component.get('cloud_output'):
            component['cloud_output'] = _recursive_make_immutable(component.get('cloud_output'))

    return Resource_State(**_mutable_json)
    
def _recursive_make_immutable(o):
    if isinstance(o, list):
        return frozenset([_recursive_make_immutable(x) for x in o])
    elif isinstance(o, dict):

        if "id" in o:
            if o.get('id') == 'cdev_cloud_output':
                
                tmp = {k: _recursive_make_immutable(v) for k, v in o.items()}
                if not o.get('output_operations'):
                    return frozendict(tmp)

                correctly_loaded_output_operations = _load_cloud_output(o.get('output_operations'))

                tmp['output_operations'] = correctly_loaded_output_operations
                

                return frozendict(tmp)


        return frozendict({k: _recursive_make_immutable(v) for k, v in o.items()})
    return o


def _load_cloud_output(cloud_output_operations: List[List]):
    # return the cloud output operations as tuples
    
    return tuple(
        [
            (x[0], tuple(x[1]), frozendict(x[2])) for x in cloud_output_operations
        ]
    )
