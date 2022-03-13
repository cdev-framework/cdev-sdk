"""Module that contains functionality to manage the understanding of packages within this `Workspace`
"""

import os
from pathlib import Path
import pkg_resources
from pydantic.types import DirectoryPath, FilePath
from sortedcontainers.sorteddict import SortedDict
import sys
from typing import List, Set, Dict, Tuple, Union, Optional

from serverless_parser import parser as cdev_parser

from . import docker_package_builder
from .utils import PackageTypes, ModulePackagingInfo, environment_to_architecture_suffix, Architecture

from core.utils.platforms import lambda_python_environment, get_current_closest_platform
from core.utils.logger import log

# Keep cache of already seen package names
PACKAGE_CACHE = {}

# There isn't a great runtime way of identifying python standard libraries (non C builtin libraries packaged with python).
# So I scraped the information from the python documentation website using the ./scripts/list-python-builtins
STANDARD_LIBRARY_FILES = ["3_7", "3_8", "3_9"]

# Build a dict of pkg name to pip package obj so you don't have to loop over all the packages when doing a look up
# We need to include both a the project name and 'toplevel' name. This is because a project can have a python unsafe name
# so it is allowed to have a different name that is used when importing the package in an actual python file. Both need to
# be include because, when the package is reference directly in a file it will have the top name, but when it is referenced
# as the dependency of another project it will be a the project name.
MOD_NAME_TO_PRJ_OBJ: Dict[str, pkg_resources.Distribution] = {}

PRJ_NAME_TO_TOP_LEVEL_MODULES: Dict[str, List[str]] = {}

PLATFORM_DEPENDENT_PROJECTS = set()

_already_checked_cache = set()

download_package_location = None

target_platform = get_current_closest_platform()
CURRENT_PLATFORM = get_current_closest_platform()

#_current_working_dir = CDEV_SETTINGS.get("CURRENT_PARSING_DIR")
# TODO: Make this a setting
_current_working_dir = os.getcwd()

environment_to_python_std = {
    lambda_python_environment.py37: "3_7",
    lambda_python_environment.py38_x86_64: "3_8",
    lambda_python_environment.py38_arm64: "3_8",
    lambda_python_environment.py39_x86_64: "3_9",
    lambda_python_environment.py39_arm64: "3_9",
    lambda_python_environment.py3_x86_64: "3_9",
    lambda_python_environment.py3_arm64: "3_9",
}


def _is_platform_compatible(tags: List[str]) -> bool:
    # https://packaging.python.org/specifications/platform-compatibility-tags/
    # PEP 600
    interpreter_tag = tags[0]
    platform_tag = tags[-1]

    if not (interpreter_tag[:2] == "py" or interpreter_tag[:2] == "cp"):
        # Not a cpython or generic python package
        raise Exception

    if platform_tag == "any":
        return True

    if "win32" in platform_tag:
        return False

    elif "macosx" in platform_tag:
        return False

    else:
        #Linux specific package
        return False


for project_obj in pkg_resources.working_set:
    # We need to compute some information about the available modules in the current environment. This will help to provide information about
    # the modules when handlers reference them.

    # Compute:
    # MOD_NAME_TO_PRJ_OBJ -> Dict from the module name to the project object that contains the metadata about the project the module is from
    # PRJ_NAME_TO_TOP_LEVEL_MODULES -> Dict from the project name to all of its top level modules which are used when including the project as a dependency
    # INCOMPATIBLE_PROJECTS -> Projects that are not platform agnostic and would therefore need to be redownloaded for the correct deployment architecture 

    # For information on this object check
    # https://setuptools.pypa.io/en/latest/pkg_resources.html#distribution-objects
    # Distribution Object

    # find the dist info directory that will contain metadata about the package
    dist_dir_location = os.path.join(
        project_obj.location,
        f"{project_obj.project_name.replace('-', '_')}-{project_obj.parsed_version}.dist-info",
    )
    toplevel_file_location = os.path.join(dist_dir_location, "top_level.txt")
    wheel_info = os.path.join(dist_dir_location, "WHEEL")
    
    if not os.path.isdir(dist_dir_location):
        continue


    if not os.path.isfile(toplevel_file_location):
        # If not top level file is present, then assume the only top level module available is the project name
        
        MOD_NAME_TO_PRJ_OBJ[project_obj.project_name.replace('-','_')] = project_obj
        PRJ_NAME_TO_TOP_LEVEL_MODULES[project_obj.project_name] = [
            project_obj.project_name.replace("-", "_")
        ]
        continue

    with open(toplevel_file_location) as fh:
        top_level_mod_names = fh.readlines()

        for top_level_mod_name in top_level_mod_names:
            MOD_NAME_TO_PRJ_OBJ[top_level_mod_name.strip()] = project_obj

        potential_modules = [x.strip() for x in top_level_mod_names]
        actual_modules = []
        for potential_module in potential_modules:
            # The module could be either a folder (normal case) or a single python file (ex: 'six' package)
            # If it can not be found as either than there is an issue
            potential_dir = os.path.join(project_obj.location, potential_module)
            potential_file = os.path.join(
                project_obj.location, potential_module + ".py"
            )

            if not os.path.isdir(potential_dir) and not os.path.isfile(potential_file):
                # print(f"Could not find module {potential_module} at {dist_dir_location}")
                continue

            actual_modules.append(potential_module)

        PRJ_NAME_TO_TOP_LEVEL_MODULES[project_obj.project_name] = actual_modules

    with open(wheel_info) as fh:
        lines = fh.readlines()

        # https://www.python.org/dev/peps/pep-0425/
        # if it is not pure it should only have one tag
        # We are going ot check the tags of the package to make sure it is compatible with the target deployment platform
        tags = (
            [x.split(":")[1] for x in lines if x.split(":")[0] == "Tag"][0]
            .strip()
            .split("-")
        )

        if not _is_platform_compatible(tags):
            PLATFORM_DEPENDENT_PROJECTS.add(project_obj.project_name)

######################
##### Helper Functions
######################

def _load_aws_packages(version="3_6"):
    """Returns the given built in third party packages for a given platform

    Args:
        version (str, optional): [description]. Defaults to "3_6".

    Returns:
        set[str]: modules
    """
    return set(["boto3", "botocore"])


def _load_mod_to_prj():
    return MOD_NAME_TO_PRJ_OBJ


def _load_standard_library_information(version="3_6"):
    FILE_LOC = os.path.join(
        os.path.dirname(__file__), "standard_library_names", f"python_{version}"
    )

    if not os.path.isfile(FILE_LOC):
        # TODO throw error
        raise FileNotFoundError

    with open(FILE_LOC) as fh:
        return set(fh.read().splitlines())

def _clear_already_checked_cache(starting_location: str):
    # Add the starting file of the recursive calls
    global _already_checked_cache

    _already_checked_cache = set()

    _already_checked_cache.add(starting_location)

##########################
##### Main Entry Point
##########################

def get_top_level_module_info(
    modules: List[str], start_location: FilePath, target_platform_param: lambda_python_environment, download_package_location_param: DirectoryPath = None,
) -> Dict[str, ModulePackagingInfo]:
    """Given a set of modules, find the information needed to package those modules. 

    Args:
        modules (List[str]): Module names used to by a handler
        target_platform_param (lambda_python_environment): environment the function will be deployed on, which can affect what version of
        a 3rd party module is used.
        download_package_location_param (DirectoryPath): Base Directory that any downloaded package from Docker will be stored.

    Returns:
        module_infos (SortedDict[str, ModulePackagingInfo]): Dict (Sorted by module name) of the module information
        objects


    A handler file will have a set top level modules that are defined at the top of the file. We need to determine the module information
    about these and then return them in a way that allows them to be packaged efficiently. 


    """
    
    # Set the global value for the recursive function to use
    global download_package_location
    download_package_location = download_package_location_param

    global target_platform
    target_platform = target_platform_param

    log.debug('Getting Module Packaging Info for modules %s for target platform %s', modules, target_platform)
    
    all_packages = {}

    # we want to keep a cache of files we have already checked to speed up the process
    # clear this cache between iterations to make sure no files have changed
    _clear_already_checked_cache(start_location)

    for module_name in modules:
        all_packages[module_name] = _get_module_info(module_name, start_location)

    return SortedDict(all_packages)


def _get_module_info(
    module_name: str, original_file_location: str
) -> ModulePackagingInfo:
    """Create the information needed to package this dependency with a parsed function. 
    
    Args:
        module_name (str): The module name to look up. It can also be a relative name (begins with '.')
        original_file_location (str): Since the module name can be a relative import it needs to have the location of the
        starting location to help resolve the reference

    Returns
        info (ModulePackagingInfo): information for the packages to package

    We use the recursive method because we must compute the package information for the dependencies of this dependency. 
   
    """
    log.debug('Top Getting Module Packaging Info for module %s', module_name)
    # Note the package cache is implemented at the recursive level so that recursive calls can benefit from the cache also
    info = _recursive_create_module_package_info(module_name, original_file_location)

    log.debug('Top Recieve Module Packaging Info %s for module %s', info, module_name)

    return info





def _recursive_create_module_package_info(
    module_name: str, original_file_location: str
) -> ModulePackagingInfo:
    """Recursively create a module information object by finding out what type of module this is, and then recursively creating
    any dependant modules.

    Args:
        module_name (str): This is the top level module name used by the handler (can be a relative module)
        original_file_location: Location to use as start point if a local module is given

    Returns:
        module_info (ModulePackagingInfo): Information object for the given module

    """

    global download_package_location
    global target_platform

    if (module_name, original_file_location) in PACKAGE_CACHE:
        # Look in the cache if there is already information about this module to speed up the process
        log.debug('Package CACHE HIT for  (%s,%s)', module_name, original_file_location)
        return PACKAGE_CACHE.get((module_name, original_file_location))

    if (
        not module_name in sys.modules
        and not module_name in MOD_NAME_TO_PRJ_OBJ
        and not module_name[0] == "."
    ):
        # The module name is not in the available system modules and also not a relative module
        
        raise Exception(f"Bad module name {module_name}; Not a sys module, relatively referenced package, or pip installed package")

    else:
        standard_lib_info = _load_standard_library_information(environment_to_python_std.get(target_platform))
        aws_packages = _load_aws_packages(environment_to_python_std.get(target_platform))
        pip_packages = _load_mod_to_prj()

        if module_name in standard_lib_info:
            # Module is from the standard library
            log.debug('Standard Library: %s', module_name)
            rv = ModulePackagingInfo(
                **{
                    "module_name": module_name,
                    "type": PackageTypes.STANDARDLIB,
                    "version_id": None,
                    "fp": None,
                }
            )

        elif module_name in aws_packages:
            # Module is part of the default libraries available in the aws lambda python environment
            log.debug('Library included with runtime environment: %s', module_name)
            rv = ModulePackagingInfo(
                **{
                    "module_name": module_name,
                    "type": PackageTypes.AWSINCLUDED,
                    "version_id": None,
                    "fp": None,
                }
            )

        elif module_name in pip_packages:
            # Module was installed with a package manager and therefor contains additional metadata that can be used to find the dependencies
            log.debug('Pip package: %s', module_name)
            tmp_distribution_obj = pip_packages.get(module_name)

            project_name = tmp_distribution_obj.project_name

            module_arch = Architecture.ANY

            if project_name in PLATFORM_DEPENDENT_PROJECTS:
                log.debug('Pip package %s is not a universal package', module_name)
                # Some of the projects that can be installed are platform dependant and the users environment might not match the aws lambda
                # environment. So, we need to use docker to pull the compatible version of the library then use that in the final archive
                
                if CURRENT_PLATFORM and (CURRENT_PLATFORM == target_platform):
                    # IF the current platform exists and is the same as the target platform no need to download a new version
                    module_arch = environment_to_architecture_suffix.get(CURRENT_PLATFORM)
                    log.debug('Target Platform matches Current Platform (%s) for pkg %s ', target_platform, module_name)

                elif download_package_location:
                    # Else there needs to be a provided download location
                    if docker_package_builder.docker_available():
                        log.debug('User Docker to pull pkg %s ', module_name)

                        # Note that the download package function uses a cache so it will only actually pull the first time the user wants to
                        # package this function.
                        rv = docker_package_builder.download_package_and_create_moduleinfo(
                            tmp_distribution_obj,
                            target_platform,
                            module_name,
                            download_package_location
                        )
                        PACKAGE_CACHE[(module_name, original_file_location)] = rv
                        return rv

                    else:
                        raise Exception("Trying to target an architecture with a dependant package but Docker is not available")

                else:
                    raise Exception("Trying to target an architecture with a dependant package but have Docker is not allowed")

            # The package could be either a folder (normal case) or a single python file (ex: 'six' package)
            # If it can not be found as either than there is an issue
            potential_dir = os.path.join(
                pip_packages.get(module_name).location, module_name
            )
            potential_file = os.path.join(
                pip_packages.get(module_name).location, module_name + ".py"
            )

            if os.path.isdir(potential_dir):
                tmp_fp = potential_dir
            elif os.path.isfile(potential_file):
                tmp_fp = potential_file
            else:
                raise Exception

            log.debug("Final fp for %s -> %s", module_name, tmp_fp)

            # Find the dependent modules for this project (distribution obj)
            (
                tmp_dependencies_flat,
                tmp_dependencies_tree,
            ) = _recursive_check_for_dependencies_project(tmp_distribution_obj)


            log.debug("Flat dependencies for %s -> %s", module_name, tmp_dependencies_flat)
            log.debug("Tree dependencies for %s -> %s", module_name, tmp_dependencies_tree)
            
            rv = ModulePackagingInfo(
                **{
                    "module_name": module_name,
                    "type": PackageTypes.PIP,
                    "arch": module_arch,
                    "version_id": tmp_distribution_obj.version,
                    "fp": tmp_fp,
                    "flat": tmp_dependencies_flat,
                    "tree": tmp_dependencies_tree,
                }
            )

        else:
            # Since the module is not in the PIP, platform builtins, or std lib
            # It should be treated as a local package
            mod = sys.modules.get(module_name)
            if mod:
                if not mod.__file__:
                    # if the module __file__ is not present than it is a builtin module to the interpreter
                    tmp_type = PackageTypes.BUILTIN
                    tmp_fp = None
                    tmp_version = None
                else:
                    # this is a local package that was not imported using a relative path
                    tmp_type = PackageTypes.LOCALPACKAGE
                    tmp_version = None

                    if mod.__file__.split("/")[-1] == "__init__.py":
                        tmp_fp = os.path.dirname(mod.__file__)
                    else:
                        tmp_fp = mod.__file__
                    # TODO: Maybe support this in the future
                    log.debug("Local absolute reference for module %s", module_name)

                    raise Exception(f"{module_name}: Referencing local package using absolute import statement. Change it to a relative import to work with Cdev.")
            elif module_name[0] == ".":
                # IF the module name started with a '.' then it is a relative import
                
                tmp_type = PackageTypes.LOCALPACKAGE
                original_path = Path(original_file_location)

                tmp_version = None

                tmp_module_name = module_name

                levels = 0
                # loop to compute how many layers up this relative import is by popping off the '.' char
                # until it reaches a different char
                while tmp_module_name[0] == ".":
                    tmp_module_name, next_char = tmp_module_name[1:], tmp_module_name[0]

                    if next_char == ".":
                        levels = levels + 1
                    else:
                        break
                
                log.debug("%s if %s levels up from handler", module_name, levels)

                # go up the amount of levels need to get to the top of the search path
                relative_base_dir = original_path.parents[levels - 1]

                # since we popped off the leading '.' chars, the remaining portion is the path to search down from the top
                tmp_pkg_path_parts = tmp_module_name.split(".")

                # Again the module can either be a single file or a directory containing other files
                tmp_potential_file = os.path.join(
                    relative_base_dir,
                    "/".join(tmp_pkg_path_parts[:-1]),
                    tmp_pkg_path_parts[-1] + ".py",
                )
                tmp_potential_dir = os.path.join(
                    relative_base_dir, "/".join(tmp_pkg_path_parts)
                )

                if os.path.isfile(tmp_potential_file):
                    tmp_fp = tmp_potential_file
                    
                elif os.path.isdir(tmp_potential_dir):
                    tmp_fp = tmp_potential_dir
                else:
                    raise Exception

                log.debug("Final relative file location (%s) from workspace to %s", tmp_fp, module_name)
                

            else:
                raise Exception(f"Unmanageable module name for local module {module_name}")

            # Since this is a local package, it does not contain any extra metadata. This means the only way to find the dependencies is to
            # parse each python file in the needed module and look at its imports :/
            (
                dependencies_flat,
                dependencies_tree,
            ) = _recursive_check_for_dependencies_package(tmp_fp)
            log.debug("Flat dependencies for %s -> %s", module_name, dependencies_flat)
            log.debug("Tree dependencies for %s -> %s", module_name, dependencies_tree)

            rv = ModulePackagingInfo(
                **{
                    "module_name": module_name,
                    "type": tmp_type,
                    "version_id": tmp_version,
                    "fp": tmp_fp,
                    "flat": dependencies_flat,
                    "tree": dependencies_tree,
                }
            )

        PACKAGE_CACHE[(module_name, original_file_location)] = rv
        log.debug("Add to cache (%s,%s) => %s", module_name, original_file_location, rv)
        return rv


def _recursive_check_for_dependencies_project(
    project_distribution_obj: pkg_resources.Distribution,
) -> Tuple[List[ModulePackagingInfo], List[ModulePackagingInfo]]:
    """
    Create the ModulePackagingInfo objects for all dependencies of this project. By calling the '_recursive_create_module_package_info' to create the
    ModulePackagingInfo objects, it creates a recursive stack that eventually leads to tmp_flat being a list of ALL needed dependencies and the tmp_tree
    to be the first level in the dependency tree for this project.

    Args:
        project_distribution_obj (pkg_resources.Distribution): object from pkg_resources that contains metadata on this package

    Returns:
        flat (List[ModulePackagingInfo]): List of ALL needed dependencies
        tree (List[ModulePackagingInfo]): First level of a dependency tree for this project
    """
    tmp_flat = set()
    tmp_tree = set()

    for project_obj in project_distribution_obj.requires():

        if project_obj.project_name in PRJ_NAME_TO_TOP_LEVEL_MODULES:
            project_name = project_obj.project_name

        # Note that pip packages should list their dependencies as the project name, but some use the top level module name that
        # can be slightly different than the project name.
        # Example awswrangler (2.12.1) lists 'Requires-Dist: pymysql (>=0.9.0,<1.1.0)' but the actual package name is 'PyMySQL'
        # .....python packaging sucks
        elif project_obj.project_name in MOD_NAME_TO_PRJ_OBJ:
            project_name = MOD_NAME_TO_PRJ_OBJ.get(
                project_obj.project_name
            ).project_name
        else:
            raise Exception

        top_level_modules = PRJ_NAME_TO_TOP_LEVEL_MODULES.get(project_name)
        
        for req in top_level_modules:

            tmp_dep = _recursive_create_module_package_info(req, None)
            tmp_flat.add(tmp_dep)
            tmp_tree.add(tmp_dep)

            if tmp_dep.flat:
                tmp_flat = tmp_flat.union(set(tmp_dep.flat))

    return tmp_flat, tmp_tree


def _recursive_check_for_dependencies_package(
    fp: Union[FilePath, DirectoryPath]
) -> Tuple[List[ModulePackagingInfo], List[ModulePackagingInfo]]:
    """Create the ModulePackagingInfo objects for all dependencies of a local module. 
    
    By calling the '_recursive_create_module_package_info' to create the ModulePackagingInfo objects,
    it creates a recursive stack that eventually leads to tmp_flat being a list of ALL needed dependencies 
    and the tmp_tree to be the first level in the dependency tree for this project.

    Args:
        fp (Union[FilePath, DirectoryPath]): object from pkg_resources that contains metadata on this package

    Returns:
        flat (List[ModulePackagingInfo]): List of ALL needed dependencies
        tree (List[ModulePackagingInfo]): First level of a dependency tree for this project
    """
    tmp_flat = set()
    tmp_tree = set()

    required_items = _get_local_package_dependencies(fp)

    for req in required_items:
        starting_location = fp if not req[1] else req[1]

        tmp_dep = _recursive_create_module_package_info(req[0], starting_location)

        tmp_flat.add(tmp_dep)
        tmp_tree.add(tmp_dep)

        if tmp_dep.flat:
            tmp_flat = tmp_flat.union(set(tmp_dep.flat))

    return list(tmp_flat), tmp_tree


def _get_local_package_dependencies(
    fp: Union[FilePath, DirectoryPath]
) -> List[Tuple[str, Optional[str]]]:
    """
    Get the local dependencies for a given local module by searching through the file(s) that make up the module and looking
    for import statements.

    Args:
        fp (Union[FilePath, DirectoryPath]): the location of the module in question

    Returns:
        dependencies (List[Tuple[str,str]]): List of dependant module names and an optional filepath if the module is a relative module


    Uses the Serverless Parser library to find all the imports in a given file.
    """
    global _current_working_dir

    if not _current_working_dir:
        # This setting should be set
        raise Exception

    # Since we are just reading the files not importing them. We do not have a guarantee to not cause a circular dependency
    # Therefore, we preload all the files we are going to check before checking them, and add that to a cache to check against
    # If a file is already in the cache, it means it has/or will be accounted for.

    if fp in _already_checked_cache:
        # We have already included this file so skip it
        return []

    # Local Module can be either directory or single file
    if os.path.isdir(fp):
        module_names = set()

        for dir, _, files in os.walk(fp):
            if dir in _already_checked_cache:
                continue

            # Load the directory (and subdirectories)
            _already_checked_cache.add(dir)

            for file in files:
                if not file[-3:] == ".py":
                    continue

                # Load the files
                if os.path.join(dir, file) in _already_checked_cache:
                    continue

                _already_checked_cache.add(os.path.join(dir, file))

                module_names = module_names.union(
                    cdev_parser.parse_file_for_dependencies(os.path.join(dir, file))
                )
                log.debug("Found dependent modules %s for %s", module_names, os.path.join(dir, file))

    else:
        _already_checked_cache.add(fp)
        module_names = cdev_parser.parse_file_for_dependencies(fp)
        
    log.debug("Found dependent modules %s for %s", module_names, fp)

    return list(module_names)




