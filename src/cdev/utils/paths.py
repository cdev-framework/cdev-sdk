import os

from pydantic.types import FilePath

from cdev import settings as cdev_settings

def get_relative_to_project_path(fullpath) -> str:
    return os.path.relpath(fullpath, start=cdev_settings.SETTINGS.get("BASE_PATH"))


def get_full_path_from_project_base(relative_path: str) -> FilePath:
    return os.path.join(os.path.dirname(cdev_settings.SETTINGS.get("INTERNAL_FOLDER_NAME")), relative_path)

def get_full_path_from_internal_folder(relative_path: str) -> FilePath:
    return os.path.join(cdev_settings.SETTINGS.get("INTERNAL_FOLDER_NAME"), relative_path)