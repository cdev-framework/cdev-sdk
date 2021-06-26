import importlib
import os
import sys
from cdev.cparser.parser_objects import file_information

from cdev.settings import SETTINGS as cdev_settings
from cdev.fs_manager import finder, writer

from . import state_manager as local_state_manager

# This file defines the way that a project is parsed and exectued to produce the frontend state 

class Cdev_Project():
    _instance = None
    _components = []
    _state = None

    def __new__(cls, name):
        if cls._instance is None:
            #print(f'Creating the Cdev Proejct object -> {name}')
            cls._instance = super(Cdev_Project, cls).__new__(cls)
            # Put any initialization here.
        else:
            # Raise Error
            print("SECOND TIME")


        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('HAVE NOT CREATED PROJECT OBJECT YET')
        return cls._instance


    def add_component(self, component):
        if not isinstance(component, Cdev_Component):
            # TODO Throw Error
            print(f"CANT ADD THIS COMPONENT -> {component}")
            return 
        
        self._components.append(component)

    def add_components(self, components):
        if not isinstance(components, list):
            return 

        for component in components:
            try:
                self.add_component(component)
            except Exception as e:
                print(e)
        

    def get_components(self):
        return self._components


class Cdev_Component():
    def __init__(self, name) -> None:
        self.name = name
        pass

    def render(self):
        pass

    def get_name(self):
        return self.name


class Cdev_FileSystem_Component(Cdev_Component):

    def __init__(self, fp, name):
        super().__init__(name)
        self.fp = fp

    def render(self):
        return finder.parse_folder(self.fp, self.get_name())

    



def execute_cdev_project():
    CDEV_PROJECT_FILE = _get_cdev_project_file()
    BASEDIR = os.path.dirname(CDEV_PROJECT_FILE)

    # This creates the singleton Cdev_Project object 
    _import_project_file(CDEV_PROJECT_FILE)

    ALL_COMPONENTS = Cdev_Project.instance().get_components()
    actions = {
        "appends": [],
        "deletes": [],
        "updates": []
    }

    # Generate the local diffs
    for component in ALL_COMPONENTS:
        if isinstance(component, Cdev_FileSystem_Component):
            rv = component.render()
            #print(rv)
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