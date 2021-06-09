import json
import os
import time

from cdev.settings import SETTINGS as cdev_settings
from cdev.schema import utils as schema_utils
from cdev.fs_manager import writer as cdev_writer

BASE_PATH = cdev_settings.get("BASE_PATH")

STATE_FOLDER_LOCATION = cdev_settings.get("STATE_FOLDER") 
LOCAL_STATE_LOCATION = cdev_settings.get("LOCAL_STATE_LOCATION")

FULL_LOCAL_STATE_PATH = os.path.join(BASE_PATH, LOCAL_STATE_LOCATION)

def update_local_state(project_info):
    # Returns a dictionary with the actions taken to update the local state
    # RV: {
    #   "appends": [], these are the completely new resources
    #   "deletes": [], these are the resources that are removed
    #   "updates": [], these are the resources that were updated 
    # }

    previous_local_state = _load_local_state()

    if not previous_local_state:
        # IF there was no previous local state then write the entire state as appends
        rv = _write_full_local_state(project_info)

        return rv

    # get the pure diffs in the current project and previous local state
    diffs = _get_diffs_in_local_state(project_info, previous_local_state)

    seen_paths = {}
    updates = []
    additions = []

    # We want to construct updates based on the idea if there is an addition and deletion to the same 
    # parsed path meaning that parsed path was updated.

    for deleted_function in diffs.get('deletes'):
        try:
            seen_paths[deleted_function.get('parsed_path')] = deleted_function
            os.remove(deleted_function.get('parsed_path'))
            previous_local_state.get('functions').remove(deleted_function)
        except Exception as e:
            # TODO THROW BETTER ERROR
            print(f"BAD DELETE ITEM {e}")

    for d in diffs.get("appends"):
        parsed_path = cdev_writer.write_intermediate_file(d.get("original_path"), d)

        tmp_obj = {
            "original_path": d.get("original_path"),
            "parsed_path": parsed_path,
            "hash": d.get("hash"),
            "local_function_name": d.get("function_name"),
            "timestamp": str(time.time()),
            "configuration": [
                {
                    "name": "Runtime",
                    "value": "python3.7"
                }
            ]
        }

        previous_local_state.get("functions").append(tmp_obj)

        if parsed_path in seen_paths:
            updates.append(tmp_obj)
            diffs.get('deletes').remove(seen_paths.get(parsed_path))
        else:
            additions.append(tmp_obj)

        

    diffs['updates'] = updates
    diffs['appends'] = additions

    _write_local_state(previous_local_state)

    return diffs


def _write_full_local_state(project_info):
    # NO previous local state so write current state and don't worry about diffs
    print('DO ALL CURRENT STATE')
    final_function_info = []

    for file_info in project_info:
        file_name = file_info.get("filename")

        for function_info in file_info.get('function_information'):
            parsed_path = cdev_writer.write_intermediate_file(file_name, function_info)


            tmp_obj = {
                "original_path": file_name,
                "parsed_path": parsed_path,
                "hash": function_info.get("hash"),
                "local_function_name": function_info.get("function_name"),
                "timestamp": str(time.time()),
                "configuration": [
                    {
                        "name": "Runtime",
                        "value": "python3.7"
                    }
                ]
            }

            final_function_info.append(tmp_obj)


    final_state = {
        "functions": final_function_info
    }

    _write_local_state(final_state)

    return {'appends': final_function_info}


def _get_diffs_in_local_state(project_info, previous_local_state):
    # This only returns all changes as either deletes or appends

    # For example, changing the src code of a handler results in a delete and append because
    # the old version is deleted and a new version created. It helps to have this primitive view
    # because it can be used to construct more advanced states like updates. Any advanced change 
    # to state can be constructed from these primitives

    diffs = {
        'appends': [],
        'deletes': []
    }

    for file_info in project_info:
        file_name = file_info.get("filename")

        for function_info in file_info.get('function_information'):
            hashed = function_info.get("hash")

            if hashed in previous_local_state.get("hash_to_function"):
                previous_local_state.get("hash_to_function").pop(hashed)
                continue

            function_info["original_path"] = file_name
            diffs.get('appends').append(function_info)

    for remaining in previous_local_state.get("hash_to_function"):
        diffs.get('deletes').append(previous_local_state.get('hash_to_function').get(remaining))
   
    return diffs
        
    
def _write_local_state(state):
    try:
        state.pop('hash_to_function')
    except Exception as e:
        print(f"ERROR -> {e}")

    with open(FULL_LOCAL_STATE_PATH, 'w') as fp:
        json.dump(state, fp, indent=4)


def _load_local_state():
    # TODO Make this a class and json representation use json schema 
    if not os.path.isfile(FULL_LOCAL_STATE_PATH):
        # TODO Throw error
        return None


    with open(FULL_LOCAL_STATE_PATH) as fp:
        rv = json.load(fp)

    rv['hash_to_function'] = {}

    for function_state in rv.get("functions"):
        schema_utils.validate(schema_utils.SCHEMA.FRONTEND_FUNCTION, function_state)

        rv['hash_to_function'][function_state.get("hash")] = function_state

    return rv