"""Utilities to help work with filesystem paths within the framework.


To make projects work on multiple developers machines, it is important that paths that
need to be stored in the state be written as relative paths. The relative paths can be
started from two places: Workspace and Intermediate.

The Workspace base is the base folder for all information that is unique to the current work
space. This will be default be the directory that a cli command is issued from. Changing
this value should be done with caution and understanding of how to framework/cli bootstraps
itself.


The Intermediate base is the base folder for any artifacts that are created by the framework
that need to be uploaded to the cloud. Any file made in this folder should be able to be deleted
and recreated without affecting the larger framework. Right now this folder will be within the
wWorkspace folder, but it is helpful to have the location as a seperate entity to make it possible
in the future to have a smart implementation of a cache of artifacts that can be shared across multiple
workspaces.



TODO: Make a custom type that denotes a path is a relative path to the workspace.
This could be a pydantic type that way the constraints are validated at runtime.
This is a important part to improve the DX of the working with library.
"""

import os
from typing import Union

from pydantic import DirectoryPath
from pydantic.types import FilePath

from core.constructs.workspace import Workspace


def get_relative_to_workspace_path(fullpath: FilePath) -> str:
    """Generate a relative path starting from the base path of the workspace.

    Note that the given path must be a descendent of the workspace path.

    Args:
        fullpath (str): Path to convert to a relative path

    Returns:
        str: Relative to the Workspace path
    """

    base_path = Workspace.instance().settings.BASE_PATH
    return os.path.relpath(fullpath, start=base_path)


def get_relative_to_intermediate_path(fullpath: str) -> str:
    """
    Generate a relative path starting from the intermediate directory of the workspace. The given path must be a descendent of the intermediate directory.

    Args:
        fullpath (str): Path to convert to a relative path

    Returns:
        str: Relative to the intermediate path path
    """
    intermediate_path = Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION
    return os.path.relpath(fullpath, start=intermediate_path)


def get_full_path_from_workspace_base(relative_path: str) -> FilePath:
    """
    Given a relative path from the workspace path, create the full absolute path on the current filesystem.

    Args:
        relative_path (str): Relative Path from the workspace path.

    Returns:
        FilePath: Absolute path the file.
    """
    base_path = Workspace.instance().settings.BASE_PATH
    return os.path.join(
        base_path,
        relative_path,
    )


def get_full_path_from_intermediate_base(relative_path: str) -> FilePath:
    """
    Given a relative path from the intermediate folder, create the full absolute path on the current filesystem.

    Args:
        relative_path (str): Relative Path from the workspace path.

    Returns:
        FilePath: Absolute path the file.
    """
    intermediate_path = Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION
    return os.path.join(intermediate_path, relative_path)


def is_in_workspace(full_path: str) -> bool:
    """Check if a given file is within the workspace file space

    Args:
        full_path (str): The full path to check

    Returns:
        bool
    """
    base_path = Workspace.instance().settings.BASE_PATH
    return os.path.commonprefix([full_path, base_path]) == base_path


def is_in_intermediate(full_path: str) -> bool:
    """Check if a given file is within the intermediate file space

    Args:
        full_path (str): The full path to check

    Returns:
        bool
    """
    intermediate_path = Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION
    t = os.path.commonprefix([full_path, intermediate_path])
    return t == str(intermediate_path)


def get_workspace_path() -> DirectoryPath:
    """Get the Workspace path

    Returns:
        DirectoryPath: Path to workspace directory
    """
    base_path = Workspace.instance().settings.BASE_PATH
    return base_path


def get_intermediate_path() -> DirectoryPath:
    """Get the Intermediate path

    Returns:
        DirectoryPath: Path to intermediate directory
    """
    intermediate_path = Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION
    return intermediate_path


def create_path_from_workspace(desired_path: DirectoryPath) -> None:

    if not is_in_workspace(desired_path):
        raise Exception

    if os.path.isdir(desired_path):
        return

    relative_parts = get_relative_to_workspace_path(desired_path).split("/")

    create_path(get_workspace_path(), relative_parts)


def create_path(startingpath, fullpath) -> DirectoryPath:
    """This functions takes a starting path and list of child dir and makes them all

    Example

        create_path("./basedir", ["sub1", "sub2"])

        creates:\n
            ./basedir/sub1/\n
            ./basedir/sub1/sub2\n

    Returns:
        DirectoryPath: the final path

    """

    if not os.path.isdir(startingpath):
        raise Exception

    intermediate_path = startingpath

    for p in fullpath:
        if not os.path.isdir(os.path.join(intermediate_path, p)):
            os.mkdir(os.path.join(intermediate_path, p))

        intermediate_path = os.path.join(intermediate_path, p)

    return intermediate_path


def touch_file(file_path: Union[FilePath, str]) -> None:
    """Helper function to touch a file

    Args:
        file_path (FilePath)

    Raises:
        Exception: Directory does not exist
    """
    if not os.path.isdir(os.path.dirname(file_path)):
        raise Exception(
            f"Can not create {file_path} because {os.path.dirname(file_path)} is not a directory."
        )

    with open(file_path, "a"):
        pass


def mkdir(directory_path: Union[DirectoryPath, str]) -> None:
    """Create a directory if it does not already exist.

    Args:
        directory_path (DirectoryPath)
    """
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)
