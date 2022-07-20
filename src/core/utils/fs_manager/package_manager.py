from dataclasses import dataclass, field
import os
from pydantic.types import DirectoryPath, FilePath
from typing import Any, Callable, List, Set, Dict, Tuple, Union

from serverless_parser import parser as cdev_parser
from copy import copy
from functools import reduce, partial

from pathlib import Path
from pkg_resources import Distribution, WorkingSet

from .module_types import (
    ModuleInfo,
    RelativeModuleInfo,
    StdLibModuleInfo,
    PackagedModuleInfo,
)
from core.utils.operations import concatenate_to_set, combine_dictionaries

from core.utils.exceptions import cdev_core_error

#######################
##### Types
#######################
# Function to take a module name and return it as a ModuleInfo Object
module_info_creator = Callable[[str], ModuleInfo]

module_segmenter = Callable[[List[str]], Tuple[List[str], List[str], List[str]]]


#######################
##### Exceptions
#######################
@dataclass
class PackageManagerError(cdev_core_error):
    help_message: str = ""
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class PackagingError(PackageManagerError):
    help_message: str = """
    Cdev does not support locally linked python modules that are not relatively imported. Either convert the import of the module to a relative import or do not link to the module.
    """
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class SegmentError(PackageManagerError):
    help_message: str = """
    Cdev does not support locally linked python modules that are not relatively imported. Either convert the import of the module to a relative import or do not link to the module.
    """
    help_resources: List[str] = field(default_factory=lambda: [])


#######################
##### API
#######################


def create_all_module_info(
    module_names: List[str],
    start_location: FilePath,
    standard_library: Set[str],
    pkg_dependencies_data: Dict[str, Set[str]],
    pkg_locations: Dict[str, Tuple[FilePath, str]],
) -> List[ModuleInfo]:
    """Create a Module Info from the provided data about the environment.

    Args:
        module_names (List[str]): All the names of modules.
        start_location (FilePath): Base location to resolve local imports against.
        standard_library (Set[str]): Modules available in the std library
        pkg_dependencies_data (Dict[str, Set[str]]): Dependency information for the packaged modules
        pkg_locations (Dict[str, Tuple[FilePath, str]]): Location of all packaged modules

    Returns:
        List[ModuleInfo]
    """
    module_creator = partial(
        _create_module_info,
        start_location=start_location,
        standard_library=standard_library,
        packaged_module_locations_tags=pkg_locations,
    )
    module_segmenter = partial(
        _segment_module_names,
        standard_library=standard_library,
        packaged_modules=set(pkg_locations.keys()),
    )

    return _get_all_module_info(
        module_names, pkg_dependencies_data, module_segmenter, module_creator
    )


def get_packaged_modules_name_location_tag(
    working_set: WorkingSet,
) -> Dict[str, Tuple[FilePath, str]]:
    """Generate the file system location information for modules in a working set.

    Returns:
        Dict[str, FilePath]: dictionary from module name to file_system_location
    """
    return combine_dictionaries(
        [_get_packages_modules_location_tag_info(package) for package in working_set]
    )


def get_standard_library_modules(version="3_7") -> Set[str]:
    """Get the set of names of standard libraries for a given python version

    Args:
        version (str, optional): version of python. Defaults to "3_6".

    Raises:
        FileNotFoundError

    Returns:
        Set[str]: std library module names
    """
    FILE_LOC = os.path.join(
        os.path.dirname(__file__), "standard_library_names", f"python_{version}"
    )

    if not os.path.isfile(FILE_LOC):
        raise FileNotFoundError(FILE_LOC)

    with open(FILE_LOC) as fh:
        return set(fh.read().splitlines())


def create_packaged_module_dependencies(ws: WorkingSet) -> Dict[str, Set[str]]:
    """Given a working set, create a dict from all top level modules to their entire list of its dependant modules.

    Args:
        ws (WorkingSet)

    Returns:
        Dict[str, List[str]]: <module_name, all modules it depends on>
    """
    pkgs_to_top_mods = _create_pkg_to_top_modules(ws)

    return combine_dictionaries(
        [_get_module_dependencies_info(x, pkgs_to_top_mods, ws) for x in ws]
    )


#########################
##### Helper Functions
#########################
def _get_all_module_info(
    module_names: List[str],
    pkg_module_dep_info: Dict[str, Set[str]],
    module_segmenter: module_segmenter,
    module_creator: module_info_creator,
) -> List[Union[RelativeModuleInfo, StdLibModuleInfo, PackagedModuleInfo]]:
    """Given a list of modules, compute all dependent module information using the given helper functions and information.

    Args:
        module_names (List[str]): module names
        pkg_module_dep_info (Dict[str, Set[str]]): dependency information for modules
        module_segmenter (module_segmenter): segment modules into different classes
        module_creator (module_info_creator): create the Module Info

    Raises:
        Exception: _description_

    Returns:
        List[Union[RelativeModuleInfo, StdLibModuleInfo, PackagedModuleInfo]]: All Module information
    """

    cache = {}
    relative_mod_names, packaged_mod_names, std_lib_mod_names = module_segmenter(
        module_names
    )

    direct_relative_modules: List[RelativeModuleInfo] = [
        module_creator(x) for x in relative_mod_names
    ]
    direct_std_library_modules: List[StdLibModuleInfo] = [
        module_creator(x) for x in std_lib_mod_names
    ]

    # rv
    relative_modules = set(direct_relative_modules)
    std_library_modules = set(direct_std_library_modules)

    # tmp holder of the name of the pkged modules. Use names later to find all dependencies
    referenced_pkged_module_names: Set[str] = set(packaged_mod_names)

    # Find the relative dependencies in a module
    for relative_module in direct_relative_modules:
        (
            tmp_relative_module_dependencies,
            tmp_pkged_mod_names,
            tmp_std_lib_mods,
            cache,
        ) = _recursive_find_relative_module_dependencies(
            relative_module, module_segmenter, module_creator, cache
        )

        # add the newly found relative modules to the set of relative modules
        relative_modules = relative_modules.union(tmp_relative_module_dependencies)

        # add the module names of pkged modules
        referenced_pkged_module_names = referenced_pkged_module_names.union(
            tmp_pkged_mod_names
        )

        # add the std library modules
        std_library_modules = std_library_modules.union(tmp_std_lib_mods)

    # All dependencies
    all_pkged_module_names: Set[str] = set()

    # Compute the packaged module info
    for x in referenced_pkged_module_names:
        if x not in pkg_module_dep_info:
            raise Exception(f"Cant not find {x} in given pkged_modules info")

        all_pkged_module_names.add(x)
        all_pkged_module_names = all_pkged_module_names.union(
            pkg_module_dep_info.get(x)
        )

    return [
        *relative_modules,
        *[module_creator(x) for x in all_pkged_module_names],
        *std_library_modules,
    ]


def _create_module_info(
    module_name: str,
    start_location: FilePath,
    standard_library: Set[str],
    packaged_module_locations_tags: Dict[str, FilePath],
) -> ModuleInfo:
    """Given a module_name, create a ModuleInfo object based on the current environment expressed by the parameters.

    This process needs the set of standard library modules, set of packaged modules, and the base path to
    resolve relative imports against. It is recommended to create a partial function encoding this information then you have a 'module_info_creator' compatible function
    signature.

    Args:
        modules (List[str]): Module names used by a handler
        start_location (FilePath): Path to resolve relative imports against
        standard_library (Set[str]): Set of modules available as the standard library
        packaged_modules (Dict[str, FilePath]): Dict containing information needed to create a packaged module info. This is the base folder location.

    Returns:
        ModuleInfo
    """

    if module_name[0] == ".":
        return _create_relative_module_info(module_name, start_location)

    elif module_name in standard_library:
        return _create_std_library_module_info(module_name)

    elif module_name in packaged_module_locations_tags:
        location, tag = packaged_module_locations_tags.get(module_name)
        return _create_packaged_module_info(
            module_name, _get_module_abs_path(module_name, location), tag
        )

    else:
        raise PackagingError(
            error_message=f"Error with packaging module '{module_name}'."
        )


def _segment_module_names(
    module_names: List[str], standard_library: Set[str], packaged_modules: Set[str]
) -> Tuple[List[str], List[str], List[str]]:
    """Implementation of a segmenter. Segmentation is decided by the name of the modules and provided information about the environments std
    library and packaged modules.

    Args:
        module_names (List[str]): modules to segment
        standard_library (Set[str]): std library module names
        packaged_modules (Set[str]): packaged module names

    Raises:
        Exception: Can not Segment

    Returns:
        Tuple[List[str], List[str], List[str]]: Relative Modules, Packaged Modules, Std Library Modules
    """
    rv_relative_modules = []
    rv_packaged_modules = []
    rv_std_library_modules = []

    for module_name in module_names:
        if module_name[0] == ".":
            rv_relative_modules.append(module_name)

        elif module_name in standard_library:
            rv_std_library_modules.append(module_name)

        elif module_name in packaged_modules:
            rv_packaged_modules.append(module_name)

        else:
            raise SegmentError(
                error_message=f"Error with packaging module '{module_name}'."
            )

    return rv_relative_modules, rv_packaged_modules, rv_std_library_modules


def _recursive_find_relative_module_dependencies(
    module: RelativeModuleInfo,
    module_segmenter: module_segmenter,
    module_creator: module_info_creator,
    cache: Dict,
) -> Tuple[Set[RelativeModuleInfo], Set[str], Set[StdLibModuleInfo], Dict]:
    """For the given RelativeModuleInfo Object, find the information about any modules that it links to.

    Use the module_identifier to determine the type of module based on the given module name. Then use the module_creator to generate the input
    to use to recursively create any additional RelativeModuleInfo objects.

    Args:
        module (RelativeModuleInfo): provided relative module
        module_segmenter (Callable): function to segment found modules
        module_creator (module_info_creator): function to create ModuleInfo Objects

    Returns:
        Tuple[List[RelativeModuleInfo], List[str]]: Needed RelativeModuleInfos and packages module names
    """
    cache_copy = copy(cache)

    # if get_from_relative_modules_cache(module, cache_copy):
    #    # Return cached value if available
    #    print(get_from_relative_modules_cache(module, cache_copy))
    #    return get_from_relative_modules_cache(module, cache_copy)

    # Get all the directly referenced modules in the provided relative module
    direct_dependencies: List[str] = list(
        filter(
            lambda x: not x == module.module_name,
            _get_relative_package_dependencies(module.absolute_fs_position),
        )
    )

    # Segment these module names
    (
        relative_dependencies_names,
        packaged_dependencies_names,
        std_dependencies_names,
    ) = module_segmenter(direct_dependencies)

    # Sets we will add to for each type of module
    rv_relative_dependencies: Set[RelativeModuleInfo] = set(
        [module_creator(x) for x in relative_dependencies_names]
    )
    rv_std_dependencies: Set[StdLibModuleInfo] = set(
        [module_creator(x) for x in std_dependencies_names]
    )
    rv_packaged_dependencies_names: Set[str] = set(packaged_dependencies_names)

    # For the relative dependencies, Recursively find any other modules needed
    for relative_dependency in relative_dependencies_names:
        tmp = _recursive_find_relative_module_dependencies(
            module_creator(relative_dependency),
            module_segmenter,
            module_creator,
            cache_copy,
        )
        (
            tmp_relative_dependencies,
            tmp_packaged_dependencies,
            tmp_std_dependencies,
            cache_copy,
        ) = tmp

        rv_relative_dependencies.update(tmp_relative_dependencies)
        rv_packaged_dependencies_names.update(tmp_packaged_dependencies)
        rv_std_dependencies.update(tmp_std_dependencies)

    cache_copy = put_relative_modules_cache(
        module,
        (rv_relative_dependencies, packaged_dependencies_names, rv_std_dependencies),
        cache_copy,
    )
    return (
        rv_relative_dependencies,
        rv_packaged_dependencies_names,
        rv_std_dependencies,
        cache_copy,
    )


### Create Module Info Object


def _create_relative_module_info(
    module_symbol: str, original_file_location: FilePath
) -> RelativeModuleInfo:
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
    relative_level = _count_relative_level(module_symbol)

    original_path = Path(original_file_location)
    # go up the amount of levels need to get to the top of the search path
    relative_base_dir = original_path.parents[relative_level - 1]

    # remove leading '.' chars, the remaining portion is the path to search down from the top
    tmp_pkg_path_parts = str(module_symbol).lstrip(".").split(".")

    # Again the module can either be a single file or a directory containing other files
    tmp_potential_file = os.path.join(
        relative_base_dir,
        "/".join(tmp_pkg_path_parts[:-1]),
        tmp_pkg_path_parts[-1] + ".py",
    )
    tmp_potential_dir = os.path.join(relative_base_dir, "/".join(tmp_pkg_path_parts))

    if os.path.isfile(tmp_potential_file):
        fp = tmp_potential_file
        is_dir = False
    elif os.path.isdir(tmp_potential_dir):
        fp = tmp_potential_dir
        is_dir = True
    else:
        raise Exception(f"Bad relative module: {module_symbol}")

    return RelativeModuleInfo(
        module_name=module_symbol, absolute_fs_position=fp, is_dir=is_dir
    )


def _create_packaged_module_info(
    module_symbol: str, filepath: FilePath, tag: str
) -> PackagedModuleInfo:
    """Create a PackagedModuleInfo object

    Args:
        module_symbol (str): symbol used to import module
        filepath (FilePath): Filesystem location of the module
        tag (str): tags from the package

    Returns:
        PackagedModuleInfo
    """

    if os.path.isfile(filepath):
        is_dir = False
    elif os.path.isdir(filepath):
        is_dir = True

    return PackagedModuleInfo(
        module_name=module_symbol, absolute_fs_position=filepath, is_dir=is_dir, tag=tag
    )


def _create_std_library_module_info(module_symbol: str) -> StdLibModuleInfo:
    """Create a StdLibModuleInfo object

    Args:
        module_symbol (str): std library module name

    Returns:
        StdLibModuleInfo
    """
    return StdLibModuleInfo(module_name=module_symbol)


### Create package information... Dependant on Distribution or WorkingSet


def _create_pkg_to_top_modules(ws: WorkingSet) -> Dict[str, List[str]]:
    """Given a working set, create a Dict from package names to a list of the top level module names in the package

    Args:
        ws (WorkingSet):

    Returns:
        Dict[str, List[str]]: <package_name, top_level_module_names>
    """
    return combine_dictionaries(
        [{x.project_name: _create_packages_direct_modules(x)} for x in ws]
    )


def _create_packages_direct_modules(dependency: Distribution) -> List[str]:
    """Create the list of top level modules in the given Distribution.

    Args:
        dependency (Distribution)

    Returns:
        List[str]: top level modules
    """
    _, top_level_fp, _, _ = _get_metadata_files_for_package(dependency)

    if top_level_fp == None:
        # Problem when Cdev is locally linked... #TODO find more permanent solution
        return []

    if not os.path.isfile(top_level_fp):
        # If not top level file is present, then assume the only top level module available is the project name
        # modified to be python compliant
        return [dependency.project_name.replace("-", "_")]

    else:
        # Return all the names in the top level file
        with open(top_level_fp) as fh:
            top_level_mod_names = fh.readlines()

        return [x.strip() for x in top_level_mod_names]


def _get_module_dependencies_info(
    pkg: Distribution, pkg_to_top_mods: Dict[str, List[str]], ws: WorkingSet
) -> Dict[str, Set[str]]:
    """Given a package, return a dict containing the top level modules as keys and all dependant modules as the value.

    Args:
        pkg (Distribution): Distribution object
        pkg_to_top_mods (Dict[str, List[str]]): Information about a packages top level modules
        ws (WorkingSet): Working set to find the requirements for this package

    Returns:
        Dict[str, List[str]]: <module_name, dependant_module_names>
    """

    keys = pkg_to_top_mods.get(pkg.project_name)

    all_dependencies = concatenate_to_set(
        [
            list(_recursive_get_all_dependencies(ws.find(x), pkg_to_top_mods, ws))
            for x in pkg.requires()
        ]
    )

    return combine_dictionaries([{k: all_dependencies} for k in keys])


def _recursive_get_all_dependencies(
    dependency: Distribution, pkg_to_top_mods: Dict[str, List[str]], ws: WorkingSet
) -> Set[str]:
    """Given a Distribution, return all dependant modules including top level modules for the Distribution. This should
    be used when finding the provided dependency is the requirement for another package.

    Args:
        dependency (Distribution)

    Returns:
        List[str]: All module dependencies
    """
    pkg_to_top_copy = copy(pkg_to_top_mods)
    # return [*[top_modules], *[all_dependencies]]
    return concatenate_to_set(
        [
            pkg_to_top_copy.get(dependency.project_name),
            concatenate_to_set(
                [
                    _recursive_get_all_dependencies(ws.find(x), pkg_to_top_mods, ws)
                    for x in dependency.requires()
                ]
            ),
        ]
    )


def _get_packages_modules_location_tag_info(
    package: Distribution,
) -> Dict[str, FilePath]:
    """Get all the top level modules available from a given package

    Returns:
        List[Tuple[str, List[str]]]: List of tuples of (name, List[tags])
    """
    # For information on this object check
    # https://setuptools.pypa.io/en/latest/pkg_resources.html#distribution-objects
    # Distribution Object

    (
        _,
        toplevel_location,
        wheel_location,
        base_directory_location,
    ) = _get_metadata_files_for_package(package)

    if not toplevel_location or not wheel_location:
        # TODO None returned for pkgs like Cdev
        return {}

    tags = "-".join(_get_tags_from_wheel(wheel_location))

    if not os.path.isfile(toplevel_location):
        # If not top level file is present, then assume the only top level module available is the
        # project name properly converted
        return {package.project_name.replace("-", "_"): (base_directory_location, tags)}

    with open(toplevel_location) as fh:
        # read the top_level file for all the modules directly available in this package
        top_level_mod_names = fh.readlines()

    return {x.strip(): (base_directory_location, tags) for x in top_level_mod_names}


def _get_metadata_files_for_package(
    package: Distribution,
) -> Tuple[str, str, str, FilePath]:
    """Return the needed metadata about a package.

    Args:
        package (Distribution)

    Returns:
        Tuple[str,str,str, FilePath]: Distinfo_folder, TopLevel_fileloc, Wheel_fileloc, base_dir
    """

    # find the dist info directory that will contain metadata about the package
    dist_dir_location = os.path.join(
        package.location,
        f"{package.project_name.replace('-', '_')}-{package.parsed_version}.dist-info",
    )

    if not os.path.isdir(dist_dir_location):
        # raise Exception(f"No .distinfo found for {package}")
        return None, None, None, None

    toplevel_file_location = os.path.join(dist_dir_location, "top_level.txt")
    wheel_info = os.path.join(dist_dir_location, "WHEEL")

    return (
        dist_dir_location,
        toplevel_file_location,
        wheel_info,
        package.location if not package.location == "none" else None,
    )


### Helper Functions with standard inputs


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


def _get_tags_from_wheel(wheel_info_location: FilePath) -> List[str]:
    """Get the tags information from a wheels file

    Args:
        wheel_info_location (FilePath)

    Returns:
        List[str]: tags
    """
    with open(wheel_info_location) as fh:
        lines = fh.readlines()

        # https://www.python.org/dev/peps/pep-0425/
        # if it is not pure it should only have one tag
        # We are going ot check the tags of the package to make sure it is compatible with the target deployment platform
        tags = (
            [x.split(":")[1] for x in lines if x.split(":")[0] == "Tag"][0]
            .strip()
            .split("-")
        )

        return tags


def _get_module_abs_path(module_name: str, base_path: FilePath) -> FilePath:
    """Given a module and base directory to search, return either the folder or file of the module

    Args:
        module_name (str): name of imported module
        base_path (FilePath): directory to search

    Raises:
        Exception: Could not find either <module_name>.py file or folder

    Returns:
        FilePath: absolute location
    """

    potential_dir = os.path.join(base_path, module_name)
    potential_file = os.path.join(base_path, module_name + ".py")

    if os.path.isdir(potential_dir):
        return potential_dir
    elif os.path.isfile(potential_file):
        return potential_file
    else:
        raise Exception(
            f"Could not find either {module_name}.py or {module_name} directory in {base_path}"
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


#######################
##### Utilities
#######################
def get_from_relative_modules_cache(
    module: RelativeModuleInfo, cache: Dict
) -> Union[None, List[str]]:
    """Look for a relative module in a given cache

    Args:
        module (RelativeModuleInfo): module to look for
        cache (Dict): data cache

    Returns:
        Union[None, List[str]]: cached value
    """
    return cache.get(module.to_key())


def put_relative_modules_cache(
    module: RelativeModuleInfo,
    val: Tuple[Set[RelativeModuleInfo], Set[str], Set[StdLibModuleInfo]],
    cache: Dict,
) -> Dict:
    """Put the value in the cache for a given module

    Args:
        module (RelativeModuleInfo): module to use as key
        val (Tuple[Set[RelativeModuleInfo], Set[str], Set[StdLibModuleInfo]]): cache value
        cache (Dict): cache

    Returns:
        Dict: new cache
    """
    new_cache = copy(cache)

    new_cache[module.to_key()] = val

    return new_cache
