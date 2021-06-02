import json
import os

from jsonschema import validate

from cdev.settings import SETTINGS as cdev_settings
from cdev.schema import utils as schema_utils
from cdev.fs_manager import writer as cdev_writer

BASE_PATH = cdev_settings.get("BASE_PATH")

STATE_FOLDER_LOCATION = cdev_settings.get("STATE_FOLDER") 
LOCAL_STATE_LOCATION = cdev_settings.get("LOCAL_STATE_LOCATION")

FULL_LOCAL_STATE_PATH = os.path.join(BASE_PATH, LOCAL_STATE_LOCATION)

def update_local_state(project_info):
    print(project_info)
    previous_local_state = _load_local_state()
    print("---------------------------------")
    print(previous_local_state)
    print("---------------------------------")

    if not previous_local_state:
        _write_full_local_state(project_info)
        return None

    diffs = _get_diffs_in_local_state(project_info, previous_local_state)

    print(f"DIFFS -> {diffs}")

    for d in diffs.get("appends"):
        parsed_path = cdev_writer.write_intermediate_file(d.get("original_path"), d)

        tmp_obj = {
            "original_path": d.get("original_path"),
            "runtime": "python3.8",
            "parsed_path": parsed_path,
            "hash": d.get("hash"),
            "handler_name": d.get("function_name")
        }


        previous_local_state.get("functions").append(tmp_obj)

    for deleted_function in diffs.get('deletes'):
        try:
            previous_local_state.get('functions').remove(deleted_function)
            print(f"REMOVED {deleted_function}")
        except Exception as e:
            print(f"DELETING BAD ITEM {e}")

    _write_local_state(previous_local_state)


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
                "runtime": "python3.8",
                "parsed_path": parsed_path,
                "hash": function_info.get("hash"),
                "handler_name": function_info.get("function_name")
            }

            final_function_info.append(tmp_obj)


    final_state = {
        "functions": final_function_info
    }

    _write_local_state(final_state)

    return None


def _get_diffs_in_local_state(project_info, previous_local_state):
    # Need to create both the appends and deletes for the new local state 

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
        function_schema = schema_utils.get_schema("FUNCTION")
        validate(function_state, function_schema)

        rv['hash_to_function'][function_state.get("hash")] = function_state

    return rv