"""Utilities to help the framework manage writing and loading files

These utilities are used within the default implementation of the `Backend` construct
to help manage the writing and loading of resource states.

"""

import json
from pydantic import FilePath
import os
import shutil
from typing import Dict, List, Tuple
from core.constructs.cloud_output import cloud_output_dynamic_model

from core.constructs.resource_state import Resource_State
from core.utils.exceptions import cdev_core_error
from ..constructs.models import frozendict


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling immutable data

    Since we want to store state as immutable structures to make direct comparisons easier within the framework,
    we need to provide this encoder to denote how we want those structures stored as json. Using this encoder means
    that there is some information loss when making the obj a json (i.e. cant tell the difference between a frozenset vs
    list), therefor when loading the json back into the system, a custom utility should be used that reintroduces the
    immutable structures back into the data.

    Args:
        json ([type]): [description]
    """

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        if isinstance(obj, frozenset):
            return list(obj)

        if isinstance(obj, frozendict):
            return dict(obj)

        if isinstance(obj, tuple):
            print(f"Trying to serialize tuple {obj}")
            return list(obj)

        return json.JSONEncoder.default(self, obj)


def safe_json_write(obj: Dict, fp: FilePath) -> None:
    """
    Safely write files by first writing to a tmp file then copying to final location. This ensures that no file is
    partially written thus leaving a file in an unrecoverable state.

    Args:
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
        raise cdev_core_error(f"Could not write data as a json into tmp file; {obj}", e)

    try:
        shutil.copyfile(tmp_fp, fp)
    except Exception as e:
        raise cdev_core_error(
            f"Could not copy tmp file into actual location; {tmp_fp} -> {fp}", e
        )

    os.remove(tmp_fp)


def load_resource_state(fp: FilePath) -> Resource_State:
    """Load the Resource State correctly from the json file.

    Since the resource state is store as a json, it is important that it is loaded correctly from the file. This
    means that some of the nested structures need to be converted. Json only stores list and maps, so without
    custom handling of some structures, it would be impossible to load the resource state correctly.

    For the `resources`, all the structures in the list container should be loaded as immutable objects
    because they are `resource_models`.

    For the `references`, all the structures in the list container should be loaded as immutable objects
    because they are `references_models`.

    for the `cloud_output`, all the structures in the list container should be loaded as immutable objects
    because they are `cloud_output`models`. They have a special structure that needs to be preserved so that
    the execution order of the operations are preserved.

    Args:
        fp (FilePath): Path to the file storing the resource state

    Returns:
        Resource_State

    Raises:
        Cdev_Error
    """

    if not os.path.isfile(fp):
        raise cdev_core_error(
            f"Trying to load resource state from {fp} but it does not exist"
        )

    try:
        with open(fp, "r") as fh:
            _mutable_json = json.load(fh)

    except Exception as e:
        raise cdev_core_error(
            f"Trying to load resource state from {fp} but could not load the file as a json"
        )

    for component in _mutable_json["components"]:
        # The actual resource and reference models need to be immutable data structures so that they can have a
        # __hash__ value.

        try:
            if component.get("resources"):
                component["resources"] = [
                    _recursive_make_immutable(x) for x in component.get("resources")
                ]

            if component.get("references"):
                component["references"] = [
                    _recursive_make_immutable(x) for x in component.get("references")
                ]

            if component.get("cloud_output"):
                component["cloud_output"] = _recursive_make_immutable(
                    component.get("cloud_output")
                )

        except Exception as e:
            raise cdev_core_error(
                f"Trying to load resource state from {fp} but could not make dict immutable",
                e,
            )

    try:
        rv = Resource_State(**_mutable_json)
    except Exception as e:
        raise cdev_core_error(
            f"Trying to load resource state from {fp} but could not serialized Dict into Resource_State",
            e,
        )

    return rv


def _recursive_make_immutable(o):
    """Recursively transform an object into an immutable form

    This is a cdev core specific transformation that is used to convert Dict and List and other native python
    types into frozendict, frozenset, etc. The purpose is that the later set of objects are immutable in python
    and therefor can be used to directly compare against each other and be used as __hash__ able objects in
    things like dicts and `networkx` DAGs.

    Note the special case of handling Cloud Output Dict. These are identified as a dict with the key `id` that has
    a value `cdev_cloud_output`.

    Args:
        o (Any): original object

    Returns:
        transformed_os
    """

    # Note this is designed to be specifically used within the loading of a resource state. Therefor,
    # we do not much error handling and let an error in the structure of the data be passed up all the
    # way to `load_resource_state`

    if isinstance(o, list):
        return frozenset([_recursive_make_immutable(x) for x in o])
    elif isinstance(o, dict):

        if "id" in o:
            if o.get("id") == "cdev_cloud_output":

                tmp = {k: _recursive_make_immutable(v) for k, v in o.items()}
                if not o.get("output_operations"):
                    return frozendict(tmp)

                correctly_loaded_output_operations = _load_cloud_output_operations(
                    o.get("output_operations")
                )

                tmp["output_operations"] = correctly_loaded_output_operations

                return frozendict(tmp)

        return frozendict({k: _recursive_make_immutable(v) for k, v in o.items()})
    return o


def _load_cloud_output_operations(
    cloud_output_operations: List[List],
) -> Tuple[Tuple, ...]:
    """Load data in structure to conform to being a `cloud_output_operation`

    Note this is designed to be specifically used within the loading of a resource state. Therefor,
    we do not much error handling and let an error in the structure of the data be passed up all the
    way to `load_resource_state`

    Args:
        cloud_output_operations (List[List]): List version of the operations

    Returns:
        Operations: Tuple(Tuple(func_name, args, kwarg),...)
    """

    # Note this is designed to be specifically used within the loading of a resource state. Therefor,
    # we do not much error handling and let an error in the structure of the data be passed up all the
    # way to `load_resource_state`

    return tuple(
        [(x[0], tuple(x[1]), frozendict(x[2])) for x in cloud_output_operations]
    )
