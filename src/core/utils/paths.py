import os

from pydantic.types import FilePath

from .. import settings

INTERMEDIATE_FOLDER = settings.SETTINGS.get("INTERMEDIATE_FOLDER_LOCATION")


def get_relative_to_workspace_path(fullpath: str) -> str:
    """
    Generate a relative path starting from the base path of the workspace. The given path must be a descendent of the workspace path. 

    Args:
        fullpath (str): Path to convert to a relative path

    Returns:
        str: Relative to the Workspace path
    """
    return os.path.relpath(fullpath, start=settings.SETTINGS.get("BASE_PATH"))


def get_relative_to_intermediate_path(fullpath: str) -> str:
    """
    Generate a relative path starting from the intermediate directory of the workspace. The given path must be a descendent of the intermediate directory. 

    Args:
        fullpath (str): Path to convert to a relative path

    Returns:
        str: Relative to the intermediate path path
    """
    return os.path.relpath(
        fullpath, start=settings.SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION")
    )


def get_full_path_from_workspace_base(relative_path: str) -> FilePath:
    """
    Given a relative path from the workspace path, create the full absolute path on the current filesystem. 

    Args:
        relative_path (str): Relative Path from the workspace path.

    Returns:
        FilePath: Absolute path the file.
    """
    return os.path.join(
        settings.SETTINGS.get("BASE_PATH"),
        relative_path,
    )


def get_full_path_from_internal_folder(relative_path: str) -> FilePath:

    return os.path.join(
        settings.SETTINGS.get("INTERNAL_FOLDER_NAME"), relative_path
    )


def get_full_path_from_intermediate_folder(relative_path: str) -> FilePath:
    """
    Given a relative path from the intermediate folder, create the full absolute path on the current filesystem. 

    Args:
        relative_path (str): Relative Path from the workspace path.

    Returns:
        FilePath: Absolute path the file.
    """
    return os.path.join(
        settings.SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), relative_path
    )


def is_in_project(full_path: str) -> bool:
    return os.path.commonprefix(
        [full_path, settings.SETTINGS.get("BASE_PATH")]
    ) == settings.SETTINGS.get("BASE_PATH")



def get_project_path() -> FilePath:
    return settings.SETTINGS.get("BASE_PATH")




def create_path(startingpath, fullpath):
    # This functions takes a starting path and list of child dir and makes them all
    # Returns the final path

    # ex: _create_path(""./basedir", ["sub1", "sub2"])
    # creates:
    #   - ./basedir/sub1/
    #   - ./basedir/sub1/sub2

    if not os.path.isdir(startingpath):
        raise Exception

    intermediate_path = startingpath

    for p in fullpath:
        if not os.path.isdir(os.path.join(intermediate_path, p)):
            os.mkdir(os.path.join(intermediate_path, p))

        intermediate_path = os.path.join(intermediate_path, p)

    return intermediate_path
