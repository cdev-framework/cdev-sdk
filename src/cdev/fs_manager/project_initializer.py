# This file contains the functionality to initialize a folder into a project 
import os

from cdev.settings import SETTINGS as cdev_settings

INTERNAL_FOLDER_NAME = cdev_settings.get("INTERNAL_FOLDER_NAME")


INTERMEDIATE_FOLDER_NAME = cdev_settings.get("CDEV_INTERMEDIATE_FOLDER_LOCATION")
INTERMEDIATE_FUNCTIONS_FOLDER_NAME = cdev_settings.get("CDEV_INTERMEDIATE_FILES_LOCATION")

STATE_FOLDER_LOCATION = cdev_settings.get("STATE_FOLDER") 
LOCAL_STATE_LOCATION = cdev_settings.get("LOCAL_STATE_LOCATION")

CDEV_PROJECT_FILE = cdev_settings.get("CDEV_PROJECT_FILE")




def _get_needed_folder_structure(basepath):
    internal_folder_location = os.path.join(basepath, INTERNAL_FOLDER_NAME)

    intermediate_base_folder_location = os.path.join(basepath, INTERMEDIATE_FOLDER_NAME)

    intermediate_function_folder_location = os.path.join(basepath, INTERMEDIATE_FUNCTIONS_FOLDER_NAME)

    state_folder_location = os.path.join(basepath, STATE_FOLDER_LOCATION)

    return [internal_folder_location, intermediate_base_folder_location, intermediate_function_folder_location, state_folder_location]


def _get_need_files():
    return [LOCAL_STATE_LOCATION, CDEV_PROJECT_FILE]


def initialize_project(folder_path):
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


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)
