import os

from pydantic.types import FilePath

from cdev import settings as cdev_settings


INTERMEDIATE_FOLDER = cdev_settings.SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION")

def get_relative_to_project_path(fullpath) -> str:
    return os.path.relpath(fullpath, start=cdev_settings.SETTINGS.get("BASE_PATH"))

def get_relative_to_intermediate_path(fullpath) -> str:
    return os.path.relpath(fullpath, start=cdev_settings.SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"))


def get_full_path_from_project_base(relative_path: str) -> FilePath:
    return os.path.join(os.path.dirname(cdev_settings.SETTINGS.get("INTERNAL_FOLDER_NAME")), relative_path)


def get_full_path_from_internal_folder(relative_path: str) -> FilePath:
    return os.path.join(cdev_settings.SETTINGS.get("INTERNAL_FOLDER_NAME"), relative_path)


def get_full_path_from_intermediate_folder(relative_path: str) -> FilePath:
    return os.path.join(cdev_settings.SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), relative_path)


def is_in_project(full_path: str) -> bool:
    return os.path.commonprefix([full_path, cdev_settings.SETTINGS.get("BASE_PATH")]) == cdev_settings.SETTINGS.get("BASE_PATH")

def get_project_path() -> FilePath:
    return cdev_settings.SETTINGS.get("BASE_PATH")


def create_path(startingpath, fullpath):
    # This functions takes a starting path and list of child dir and makes them all
    # Returns the final path

    # ex: _create_path(""./basedir", ["sub1", "sub2"])
    # creates: 
    #   - ./basedir/sub1/
    #   - ./basedir/sub1/sub2

    if not os.path.isdir(startingpath):
        return None

    intermediate_path = startingpath

    for p in fullpath:
        if not os.path.isdir(os.path.join(intermediate_path, p)):
            os.mkdir(os.path.join(intermediate_path, p))

        intermediate_path = os.path.join(intermediate_path, p)

    return intermediate_path
