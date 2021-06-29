import importlib
import os
import sys

from sortedcontainers.sortedlist import SortedList
from cdev import schema

from cdev.settings import SETTINGS as cdev_settings
from cdev.schema import utils as schema_utils



from . import constructs
from .models import Rendered_State as frontend_rendered_state

"""
This file defines the way that a project is parsed and executed to produce the frontend state. 

The Cdev project object is the singleton that represents the information and configuration of the current Cdev Project.

"""

def execute_frontend() -> frontend_rendered_state:
    """
    This is the function that executes the code to generate a desired state for the project. 

    The order of the execution is:

    - Import the cdev project file
        - This should cause all components to be initialized
    - For each Cdev Component attached to the project 
        - Call the `render` method to get the desired resources and add that to the total state
    - Return a rendered state object
    """


    CDEV_PROJECT_FILE = _get_cdev_project_file()

    # This creates the singleton Cdev_Project object 
    _import_project_file(CDEV_PROJECT_FILE)

    ALL_COMPONENTS = constructs.Cdev_Project.instance().get_components()

    project_components_sorted = SortedList(key=lambda x: x.name)

    # Generate the local states
    for component in ALL_COMPONENTS:
        if isinstance(component, constructs.Cdev_Component):
            project_components_sorted.add(component.render())
        else:
            print("NOT FILE TYPE")

    project_hash = ":".join([x.hash for x in project_components_sorted])

    project = frontend_rendered_state(
        **{
            "rendered_components": list(project_components_sorted),
            "hash": project_hash,
        }
    )


    return project

 

def _get_cdev_project_file() -> str:
    return cdev_settings.get("CDEV_PROJECT_FILE")


def _get_module_name_from_path(fp: str) -> str:
    """
    Helper function for get the name of the python file as a importable module name
    """
    return fp.split("/")[-1][:-3]


def _import_project_file(fp: str) -> None:
    """
    This function takes in as input the path to the Cdev Project file and executes it by importing it as a module

    Importing this file as a module should create a singleton Cdev Project object with the needed components
    """
    mod_name = _get_module_name_from_path(fp)
        
    if sys.modules.get(mod_name):
        print(f"already loaded {mod_name}")
        importlib.reload(sys.modules.get(mod_name))
        
    # When the python file is imported and executed all the Component objects are initialized
    mod = importlib.import_module(mod_name)