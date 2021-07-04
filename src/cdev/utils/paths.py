import os

from cdev import settings as cdev_settings

def get_relative_to_project_path(fullpath):
    return os.path.relpath(fullpath, start=cdev_settings.SETTINGS.get("BASE_PATH"))