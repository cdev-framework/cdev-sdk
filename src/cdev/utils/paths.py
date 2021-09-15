import os

from pydantic.types import FilePath

from cdev import settings as cdev_settings

def get_relative_to_project_path(fullpath):
    return os.path.relpath(fullpath, start=cdev_settings.SETTINGS.get("BASE_PATH"))


def get_full_path_from_internal_folder(relative_path: str) -> FilePath:
    return os.path.join(cdev_settings.SETTINGS.get("INTERNAL_FOLDER_NAME"), relative_path)