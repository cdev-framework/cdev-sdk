import importlib
import os
import sys

from cdev.settings import SETTINGS as cdev_settings
from cdev.fs_manager import writer

from . import state_manager as local_state_manager

from . import constructs

"""
    This file defines the way that a project is parsed and executed to produce the frontend state. 

    The Cdev project object is the singleton that represents the information and configuration of the current Cdev Project.

"""

def execute_cdev_project():
    """
        This is the function that executes the code to generate a desired state for the project. 

        The order of the execution is:
        - Import the cdev project file
        - For each Cdev Component attached to the project 
            - Call the `render` method to get the resources 
            - Take the returned resources and diff that against the current local state
        - Return the diffs in the local state from the components 
    """


    CDEV_PROJECT_FILE = _get_cdev_project_file()

    # This creates the singleton Cdev_Project object 
    _import_project_file(CDEV_PROJECT_FILE)

    ALL_COMPONENTS = constructs.Cdev_Project.instance().get_components()
    actions = {
        "appends": [],
        "deletes": [],
        "updates": []
    }

    # Generate the local diffs
    for component in ALL_COMPONENTS:
        if isinstance(component, constructs.Cdev_FileSystem_Component):
            rv = component.render()

            new_diffs = local_state_manager.update_component_state(rv, component.get_name())

            for action_type in new_diffs:
                actions[action_type].extend(new_diffs.get(action_type))

        else:
            print("NOT FILE TYPE")

    # Modify local system to reflect changes
    for action_type in actions:
        if action_type == "updates":
            _handler_update_actions(actions.get(action_type))
        elif action_type == "appends":
            _handle_append_actions(actions.get(action_type))
        elif action_type == "deletes":
            _handle_delete_actions(actions.get(action_type))

    return actions

 
        
def _handle_append_actions(actions):
    #print(f"appends: {actions}")
    for append_action in actions:
        writer.write_intermediate_file(append_action.get("original_path"), append_action.get("needed_lines"), append_action.get("parsed_path"))
        
        if not append_action.get("dependencies_hash") == "0":
            print(f"ADD NEW DEP {append_action}")

def _handle_delete_actions(actions):
    #print(f"deletes: {actions}")
    for delete_action in actions:
        os.remove(delete_action.get("parsed_path"))


def _handler_update_actions(actions):
    #print(f"updates: {actions}")

    for update_action in actions:
        if 'SOURCE CODE' in update_action.get("action"):
            writer.write_intermediate_file(update_action.get("original_path"), update_action.get("needed_lines"), update_action.get("parsed_path"))


def _get_cdev_project_file():
    return cdev_settings.get("CDEV_PROJECT_FILE")


def _get_module_name_from_path(fp):
    return fp.split("/")[-1][:-3]

def _import_project_file(fp):
    mod_name = _get_module_name_from_path(fp)
        
    if sys.modules.get(mod_name):
        print(f"already loaded {mod_name}")
        importlib.reload(sys.modules.get(mod_name))
        
    # When the python file is imported and executed all the Cdev resources are created and registered with the
    # singleton
    mod = importlib.import_module(mod_name)