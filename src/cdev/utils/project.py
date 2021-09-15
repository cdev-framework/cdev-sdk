import importlib
import json
import os
import sys
from typing import List, Dict


from pydantic import BaseModel
from pydantic.types import FilePath

from cdev.settings import SETTINGS as cdev_settings

from cdev.constructs import Cdev_Project

from . import environment as cdev_environment

INTERNAL_FOLDER_NAME = cdev_settings.get("INTERNAL_FOLDER_NAME")


INTERMEDIATE_FOLDER_NAME = cdev_settings.get("CDEV_INTERMEDIATE_FOLDER_LOCATION")
INTERMEDIATE_FUNCTIONS_FOLDER_NAME = cdev_settings.get("CDEV_INTERMEDIATE_FILES_LOCATION")

STATE_FOLDER_LOCATION = cdev_settings.get("STATE_FOLDER") 
LOCAL_STATE_LOCATION = cdev_settings.get("LOCAL_STATE_LOCATION")

CDEV_PROJECT_FILE = cdev_settings.get("CDEV_PROJECT_FILE")
CDEV_ENVIRONMENT_INFO_FILE = cdev_settings.get("CDEV_ENVIRONMENT_INFO_FILE")


class project_definition(BaseModel):
    project_name: str
    base_dir: str
    environment_names: List[str]

    def __init__(__pydantic_self__, base_dir: str, project_name: str, environment_names: List[str]) -> None:
        """
        Represents the data needed to create a new cdev project:
        
        Parameters:
            project_name: name of the project
            base_dir: directory that the project will be initialized at. Most likely the current dir.
            environments: by default all projects come with prod, stage, dev-{user}; user can supply extra

        """
        
        super().__init__(**{
            "project_name": project_name,
            "base_dir": base_dir,
            "environment_names": environment_names
        })



def create_new_project(project_info: project_definition) -> bool:
    _initialize_project_structure(project_info.base_dir)

    for environment in project_info.environment_names:
        cdev_environment.create_environment(environment)

    # TODO set starting environment 
    cdev_environment.set_current_environment("dev_daniel")


def initialize_project() -> None:
    from cdev.mapper.cloudmapper import DefaultMapper
    _import_project_file(_get_cdev_project_file())
    Cdev_Project.instance().add_mapper(DefaultMapper())


def _initialize_project_structure(folder_path):
    if not os.path.isdir(folder_path):
        raise NotADirectoryError

    needed_folders = _get_needed_folder_structure(folder_path)

    
    for dir in needed_folders:
        if not os.path.isdir(dir):
            try:
                os.mkdir(dir)
            except BaseException as e:
                print(e)
                return False


    needed_files = _get_need_files()
    
    for f in needed_files:
        if os.path.isfile(f):
            continue
        
        try:
            touch(f)
        except BaseException as e:
            print(e)
            return False

    return True


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


def _get_needed_folder_structure(basepath):
    internal_folder_location = os.path.join(basepath, INTERNAL_FOLDER_NAME)

    intermediate_base_folder_location = os.path.join(basepath, INTERMEDIATE_FOLDER_NAME)


    state_folder_location = os.path.join(basepath, STATE_FOLDER_LOCATION)

    return [internal_folder_location, intermediate_base_folder_location, state_folder_location]


def _get_need_files():
    return [CDEV_PROJECT_FILE, CDEV_ENVIRONMENT_INFO_FILE]


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)
