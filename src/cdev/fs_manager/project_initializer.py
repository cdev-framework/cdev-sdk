# This file contains the functionality to initialize a folder into a project 
import os

INTERNAL_FOLDER_NAME = ".cdev"

INTERMEDIATE_FOLDER_NAME = "intermediate"

INTERMEDIATE_FUNCTIONS_FOLDER_NAME = "parsed_functions"



def _get_needed_folder_structure(basepath):
    internal_folder_location = os.path.join(basepath, INTERNAL_FOLDER_NAME)

    intermediate_base_folder_location = os.path.join(internal_folder_location, INTERMEDIATE_FOLDER_NAME)

    intermediate_function_folder_location = os.path.join(intermediate_base_folder_location, INTERMEDIATE_FUNCTIONS_FOLDER_NAME)

    return [internal_folder_location, intermediate_base_folder_location, intermediate_function_folder_location]


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

    return True



    
