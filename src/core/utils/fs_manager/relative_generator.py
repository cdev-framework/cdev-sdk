from functools import lru_cache
from typing import Union, List, Set, Tuple
from pydantic.types import DirectoryPath, FilePath
from pathlib import Path
import os

from serverless_parser import parser as cdev_parser
from .utils import module_segmenter


@lru_cache()
def get_all_relative_module_dependencies(
    module_path: FilePath,
) -> Tuple[List[str], List[str], List[str]]:

    _std_dependencies: Set[str] = set()
    _pkged_dependencies: Set[str] = set()
    _relative_dependencies_paths: Set[str] = set()

    _module_dir = Path(module_path).parent

    (
        _top_level_relative_dependencies_names,
        _top_level_packaged_dependencies_names,
        _top_level_std_dependencies_names,
    ) = _get_relative_module_dependencies(module_path)

    _std_dependencies.update(_top_level_std_dependencies_names)
    _pkged_dependencies.update(_top_level_packaged_dependencies_names)

    for _relative_dependency_name in _top_level_relative_dependencies_names:
        _relative_dependency_fp = _compute_relative_dependency_module(
            _relative_dependency_name, _module_dir
        )
        _relative_dependencies_paths.add(_relative_dependency_fp)

        (
            _rv_relative_dependencies_names,
            _rv_packaged_dependencies_names,
            _rv_std_dependencies_names,
        ) = get_all_relative_module_dependencies(_relative_dependency_fp)

        if _rv_relative_dependencies_names:
            _relative_dependencies_paths.update(set(_rv_relative_dependencies_names))

        _pkged_dependencies.update(_rv_packaged_dependencies_names)
        _std_dependencies.update(_rv_std_dependencies_names)

    return (
        _relative_dependencies_paths,
        _pkged_dependencies,
        _std_dependencies,
    )


def _compute_relative_dependency_module(module_name: str, module_path: FilePath) -> str:
    """Given a relative import and originating file location, return the information about the module

    Args:
        module_symbol (str): relative import
        original_file_location (FilePath): where the relative import is called from

    Raises:
        Exception: Can nto resolve relative module

    Returns:
        RelativeModuleInfo: information about the module
    """
    # relative module
    relative_level = _count_relative_level(module_name)

    # go up the amount of levels need to get to the top of the search path
    relative_base_dir = (
        module_path.parents[relative_level - 1]
        if relative_level > 3
        else module_path.parent
        if relative_level == 2
        else module_path
    )

    # remove leading '.' chars, the remaining portion is the path to search down from the top
    tmp_pkg_path_parts = module_name.lstrip(".").split(".")

    # Again the module can either be a single file or a directory containing other files
    tmp_potential_file = os.path.join(
        relative_base_dir,
        "/".join(tmp_pkg_path_parts[:-1]),
        tmp_pkg_path_parts[-1] + ".py",
    )
    tmp_potential_dir = os.path.join(relative_base_dir, "/".join(tmp_pkg_path_parts))

    if os.path.isfile(tmp_potential_file):
        return tmp_potential_file
    elif os.path.isdir(tmp_potential_dir):
        return tmp_potential_dir
    else:
        raise Exception(
            f"Bad relative module: {module_name}; {tmp_potential_dir}; {tmp_potential_file}"
        )


def _count_relative_level(module_symbol: str) -> int:
    """Given a relative package name return the nested levels based on the number of leading '.' chars

    Args:
        module_symbol (str): relative module symbol

    Returns:
        int: relative import level
    """
    module_symbol_cp = str(module_symbol)

    levels = 0
    # loop to compute how many layers up this relative import is by popping off the '.' char
    # until it reaches a different char
    while module_symbol_cp[0] == ".":
        module_symbol_cp, next_char = module_symbol_cp[1:], module_symbol_cp[0]

        if next_char == ".":
            levels = levels + 1
        else:
            break

    return levels


@lru_cache()
def _get_relative_module_dependencies(
    module_path: Path,
) -> Tuple[List[str], List[str], List[str]]:
    """For the given RelativeModuleInfo Object, find the information about any modules that it links to.

    Use the module_identifier to determine the type of module based on the given module name. Then use the module_creator to generate the input
    to use to recursively create any additional RelativeModuleInfo objects.

    Args:
        module (RelativeModuleInfo): provided relative module
        module_segmenter (Callable): function to segment found modules
        module_creator (module_info_creator): function to create ModuleInfo Objects

    Returns:
        Tuple[List[str], List[str], List[str]]: Tuple[relative_modules, packaged_modules, std_libraries]
    """

    # Get all the directly referenced modules in the provided relative module
    direct_dependencies: List[str] = _get_relative_package_dependencies(module_path)

    # Segment these module names
    (
        relative_dependencies_names,
        packaged_dependencies_names,
        std_dependencies_names,
    ) = module_segmenter(direct_dependencies)

    return (
        relative_dependencies_names,
        packaged_dependencies_names,
        std_dependencies_names,
    )


def _get_relative_package_dependencies(fp: Union[FilePath, DirectoryPath]) -> List[str]:
    """
    Get the local dependencies for a given local module by searching through the file(s) that make up the module and looking
    for import statements.

    Args:
        fp (Union[FilePath, DirectoryPath]): the location of the module in question

    Returns:
        dependencies (List[Tuple[str,str]]): List of dependant module names and an optional filepath if the module is a relative module


    Uses the Serverless Parser library to find all the imports in a given file.
    """
    # Local Module can be either directory or single file
    if os.path.isdir(fp):
        module_names = set()

        for dir, _, files in os.walk(fp):
            for file in files:
                if not file[-3:] == ".py":
                    continue

                module_names = module_names.union(
                    cdev_parser.parse_file_for_dependencies(os.path.join(dir, file))
                )

    else:
        module_names = cdev_parser.parse_file_for_dependencies(fp)

    return list(filter(None, module_names))
