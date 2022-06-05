from pydantic import DirectoryPath, FilePath
from typing import Callable, Dict, List, Tuple, Union

from .module_types import (
    ModuleInfo,
    PackagedModuleInfo,
    StdLibModuleInfo,
    RelativeModuleInfo,
)


#######################
##### Types
#######################
# Function that takes in a list of imported symbols and returns a list of ModuleInfo representing all needed modules.
module_creator_type = Callable[[List[str]], List[ModuleInfo]]

# Function to take a handler and needed local files and creates a deployment artifact and hash
handler_packager_type = Callable[
    [FilePath, List[Union[FilePath, DirectoryPath]]], Tuple[FilePath, str]
]

# Function to take a List of needed PackagedModuleInfo and create a list of deployment artifacts and hashes
packaged_module_packager_type = Callable[
    [List[PackagedModuleInfo]], List[Tuple[FilePath, str]]
]

serverless_function_optimizer_type = Callable[
    [
        FilePath,
        module_creator_type,
        handler_packager_type,
        packaged_module_packager_type,
    ],
    Tuple[FilePath, str, List[Tuple[FilePath, str]]],
]


def create_optimized_serverless_function_artifacts(
    original_file_location: FilePath,
    imported_modules: List[str],
    module_creator: module_creator_type,
    handler_packager: handler_packager_type,
    packaged_module_optimizer: packaged_module_packager_type,
    additional_handler_files_directories: List[Union[FilePath, DirectoryPath]] = [],
) -> Tuple[FilePath, str, List[Tuple[FilePath, str]]]:
    """Higher order function that encapsulates the general operations needed to create optimized Serverless Function artifacts.
    Given a file and list of needed lines, create the handler artifact with any include extra files/directories and local modules.
    Also create the needed packaged modules artifacts. All artifacts should include a hash.

    Args:
        original_file_location (FilePath): original file
        imported_modules (List[str], optional): modules imported by this parsed function. Defaults to [].
        module_creator (module_creator_type): function to create modules
        handler_packager (handler_packager_type): function to create artifacts of packaged modules
        packaged_module_optimizer (packaged_module_packager_type): function to optimize linked packaged modules.
        additional_handler_files_directories (List[Union[FilePath, DirectoryPath]], optional): additional files to add to handler artifact. Defaults to [].

    Returns:
        Tuple[
            FilePath,
            str,
            List[Tuple[FilePath, str]]
        ]: handler_archive, handler_hash, List[(dependency_archive_path, hash)]
    """
    # First handle getting all the module information for this function
    all_needed_modules = module_creator(imported_modules)

    # segment the modules into relative, packaged, and std library
    relative_modules, packaged_modules, _ = _segment_modules(all_needed_modules)

    # Create layer artifacts
    layers_information = packaged_module_optimizer(packaged_modules)

    handler_artifact, handler_hash = handler_packager(
        original_file_location,
        [
            *additional_handler_files_directories,
            *[x.absolute_fs_position for x in relative_modules],
        ],
    )

    return handler_artifact, handler_hash, layers_information


def _segment_modules(
    modules: List[ModuleInfo],
) -> Tuple[List[RelativeModuleInfo], List[PackagedModuleInfo], List[StdLibModuleInfo]]:
    """Segment a list of different module types

    Args:
        modules (List[ModuleInfo]):

    Returns:
        Tuple[
            List[RelativeModuleInfo],
            List[PackagedModuleInfo],
            List[StdLibModuleInfo]
        ]
    """

    return (
        list(filter(lambda x: isinstance(x, RelativeModuleInfo), modules)),
        list(filter(lambda x: isinstance(x, PackagedModuleInfo), modules)),
        list(filter(lambda x: isinstance(x, StdLibModuleInfo), modules)),
    )
