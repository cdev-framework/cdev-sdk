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

        with open(FULL_LOCAL_STATE_PATH, 'w') as fp:
            json.dump(final_state, fp, indent=4)

        return None

    diffs = []

    for file_info in project_info:
        file_name = file_info.get("filename")

        for function_info in file_info.get('function_information'):
            hashed = function_info.get("hash")

            for f in previous_local_state.get("functions"):
                if f.get("original_path") == file_name and f.get("handler_name") == function_info.get("function_name"):
                    if f.get("hash") == hashed:
                        break
                    
                    try:
                        previous_local_state.get("functions").remove(f)
                        diffs.append(function_info)
                        
                    except Exception as e:
                        print(e)

        print(f"DIFFS -> {diffs}")
        print(previous_local_state)

        for d in diffs:
            parsed_path = cdev_writer.write_intermediate_file(file_name, d)

            tmp_obj = {
                "original_path": file_name,
                "runtime": "python3.8",
                "parsed_path": parsed_path,
                "hash": d.get("hash"),
                "handler_name": d.get("function_name")
            }


            previous_local_state.get("functions").append(tmp_obj)

        with open(FULL_LOCAL_STATE_PATH, 'w') as fp:
            json.dump(previous_local_state, fp, indent=4)

        

        
        
    


def _load_local_state():
    # TODO Make this a class and json representation use json schema 
    if not os.path.isfile(FULL_LOCAL_STATE_PATH):
        # TODO Throw error
        return None


    with open(FULL_LOCAL_STATE_PATH) as fp:
        rv = json.load(fp)

    for function_state in rv.get("functions"):
        function_schema = schema_utils.get_schema("FUNCTION")
        validate(function_state, function_state)

    return rv