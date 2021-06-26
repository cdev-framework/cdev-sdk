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


def update_component_state(component_info, component_name):
    # This function takes in a component object and updates the local state to reflect the changes in the component 

    # Returns a dictionary with the actions taken to update the local state
    # RV: {
    #   "appends": [], these are the completely new resources
    #   "deletes": [], these are the resources that are removed
    #   "updates": [], these are the resources that were updated 
    # }

    previous_local_state = _load_local_state()

    if not previous_local_state:
        # IF there was not previous local state then write the entire state as appends
        previous_local_state = _create_local_state_file("PROJECT 1")


    if not component_name in previous_local_state.get("components"):
        # IF the component was not previously in the local state add it
        rv = _write_new_component(component_info, previous_local_state, component_name)
        return rv


    # get the pure diffs in the current component and previous local state
    pure_diffs = _get_diffs_in_local_state(component_info, previous_local_state, component_name)
    seen_paths = {}
    seen_total_hashed = {}
    updates = []
    additions = []

    # We want to construct updates based on the idea if there is an addition and deletion to the same 
    # parsed path means that function at that parsed path was updated. To support moving files to different directories,
    # we also look to see if the appends and deletes are just changes in the parsed_path (so no change in total hash)

    for deleted_function in pure_diffs.get('deletes'):
        # We want to delete all items that have been changed in the component as they will either be added back as an update or
        # the resource has actually been deleted. 
        try:
            seen_paths[deleted_function.get('parsed_path')] = deleted_function
            seen_total_hashed[deleted_function.get('total_hash')] = deleted_function
            previous_local_state.get("components").get(component_name).get('functions').remove(deleted_function)
        except Exception as e:
            # TODO THROW BETTER ERROR
            print(f"BAD DELETE ITEM {e}")

    
    for diff in pure_diffs.get("appends"):
        # We need to determine if the pure appends are updates or actual new resources
        # Updates can be:
        #   - Change in src code (change in source code hash)
        #   - Change in the dependencies (change in dependency hash)
        #   - Change in parsed path (files have been moved)
        # An Update can contain both change in src code and dependency at the same time, but 
        # an update to the file system must be exclusive to be registered as an update
        
        tmp_obj = _create_function_object(
                    original_path=diff.get("original_path"), 
                    parsed_path=diff.get("parsed_path"), 
                    src_code_hash=diff.get("source_code_hash"), 
                    dependencies_hash=diff.get("dependencies_hash"),
                    identity_hash=diff.get("identity_hash"),
                    metadata_hash=diff.get("metadata_hash"),
                    total_hash=diff.get("total_hash"),
                    local_function_name=diff.get("function_name"),
                    needed_lines=diff.get("needed_lines"),
                    dependencies=diff.get("dependencies")
                )

        previous_local_state.get("components").get(component_name).get("functions").append(tmp_obj)


        parsed_path = diff.get("parsed_path")

        tmp_obj["action"] = []
        if parsed_path in seen_paths:
            # This path was a previous parsed path so check for the change in the source code and dependency
            if not tmp_obj.get("source_code_hash") == seen_paths.get(parsed_path).get("source_code_hash"):
                tmp_obj["action"].append("SOURCE CODE")
            
            if not tmp_obj.get("dependencies_hash") == seen_paths.get(parsed_path).get("dependencies_hash"):
                tmp_obj["action"].append("DEPENDENCY")

            updates.append(tmp_obj)
            pure_diffs.get('deletes').remove(seen_paths.get(parsed_path))


        elif tmp_obj.get("total_hash") in seen_total_hashed:
            # This 
            tmp_obj["action"].append("MOVE")
            updates.append(tmp_obj)
            pure_diffs.get('deletes').remove(seen_total_hashed.get(parsed_path))
        else:
            additions.append(tmp_obj)

        

    pure_diffs['updates'] = updates
    pure_diffs['appends'] = additions

    _write_local_state(previous_local_state)

    return pure_diffs


def _create_local_state_file(project_name):
    # NO previous local state so write an empty object to the file then return the object
    project_state = {
        "components": {
        },
        "project_name": project_name
    }

    _write_local_state(project_state)

    return project_state


def _write_new_component(component_info, previous_state, component_name):
    # NO previous state for this component so write current component state as appends and dont worry about diffs
    final_function_info = []

    for file_info in component_info:
        file_name = file_info.get("filename")

        for function_info in file_info.get('function_information'):
            tmp_obj = _create_function_object(
                            original_path=file_name, 
                            parsed_path=function_info.get("parsed_path"), 
                            src_code_hash=function_info.get("source_code_hash"), 
                            dependencies_hash=function_info.get("dependencies_hash"),
                            identity_hash=function_info.get("identity_hash"),
                            metadata_hash=function_info.get("metadata_hash"),
                            total_hash=function_info.get("total_hash"),
                            local_function_name=function_info.get("function_name"),
                            needed_lines = function_info.get("needed_lines"),
                            dependencies=function_info.get("dependencies")
                        )

            final_function_info.append(tmp_obj)

    final_component_state = {
        "functions": final_function_info
    }

    previous_state.get("components")[component_name] = final_component_state

    _write_local_state(previous_state)

    return {'appends': final_function_info}


def _get_diffs_in_local_state(component_info, previous_local_state, component_name):
    # This only returns all changes as either deletes or appends

    # For example, changing the src code of a handler results in a delete and append because
    # the old version is deleted and a new version created. It helps to have this primitive view
    # because it can be used to construct more advanced states like updates. Any advanced change 
    # to state can be constructed from these primitives


    diffs = {
        'appends': [],
        'deletes': []
    }

    previous_component_state = previous_local_state.get("components").get(component_name)

    for file_info in component_info:
        file_name = file_info.get("filename")

        for function_info in file_info.get('function_information'):
            total_hash = function_info.get("total_hash")
            if total_hash in previous_component_state.get("hash_to_function"):
                previous_component_state.get("hash_to_function").pop(total_hash)
                continue

            function_info["original_path"] = file_name
            diffs.get('appends').append(function_info)


    for remaining in previous_component_state.get("hash_to_function"):
        diffs.get('deletes').append(previous_component_state.get('hash_to_function').get(remaining))

    return diffs

    
def _write_local_state(state):
    for component_name in state.get("components"):
        try:
            state.get("components").get(component_name).pop('hash_to_function')

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
        previous_data = json.load(fp)

    rv = {}

    for component_name in previous_data.get("components"):

        previous_data.get("components").get(component_name)['hash_to_function'] = {}
        
    
        for function_state in previous_data.get("components").get(component_name).get("functions"):
            schema_utils.validate(schema_utils.SCHEMA.FRONTEND_FUNCTION, function_state)

            total_hash = function_state.get("total_hash")

            previous_data.get("components").get(component_name)['hash_to_function'][total_hash] = function_state

    
    return previous_data



def _create_function_object(original_path="", parsed_path="", src_code_hash="", dependencies_hash="",
                            identity_hash="", metadata_hash="",  total_hash="", local_function_name="",
                            needed_lines=[], dependencies=[]):    
    tmp_obj = {
        "original_path": original_path,
        "parsed_path": parsed_path,
        "source_code_hash": src_code_hash,
        "dependencies_hash": dependencies_hash,
        "identity_hash": identity_hash,
        "metadata_hash": metadata_hash,
        "total_hash": total_hash,
        "local_function_name": local_function_name,
        "timestamp": str(time.time()),
        "needed_lines": needed_lines,
        "dependencies": dependencies,
        "configuration": [
            {
                "name": "Runtime",
                "value": "python3.7"
            }
        ]
    }

    return tmp_obj