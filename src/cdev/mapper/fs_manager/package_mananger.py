import os
import sys
import typing
import pkg_resources
from zipfile import ZipFile
from typing import List, Set, Dict, Tuple
import re



from cdev.settings import SETTINGS as CDEV_SETTINGS
from cdev.utils import hasher as cdev_hasher
from ..cparser import cdev_parser 

from packaging.utils import canonicalize_name
from sysconfig import get_platform

from . import docker_package_builder
from .utils import PackageTypes, ModulePackagingInfo, lambda_python_environments

# Keep cache of already seen package names
PACKAGE_CACHE = {}

# There isn't a great runtime way of identifying python standard libraries (non C builtin libraries packaged with python).
# So I scraped the information from the python documentation website using the ./scripts/list-python-builtins
STANDARD_LIBRARY_FILES = ['3_6', "3_7", "3_8"]

# Build a dict of pkg name to pip package obj so you don't have to loop over all the packages when doing a look up
# We need to include both a the project name and 'toplevel' name. This is because a project can have a python unsafe name
# so it is allowed to have a different name that is used when importing the package in an actual python file. Both need to 
# be include because, when the package is reference directly in a file it will have the top name, but when it is referenced
# as the dependency of another project it will be a the project name. 
MOD_NAME_TO_PRJ_OBJ: Dict[str, pkg_resources.Distribution] = {}

PRJ_NAME_TO_PRJ_OBJ: Dict[str, pkg_resources.Distribution] = {}


PRJ_NAME_TO_TOP_LEVEL_MODULES: Dict[str, List[str]] = {}

DIFF_PROJECT_TO_TOP = {}

DEPLOYMENT_PLATFORM = CDEV_SETTINGS.get("DEPLOYMENT_PLATFORM")

INCOMPATIBLE_PROJECTS = set()

def is_platform_compatible(tags: List[str]) -> bool:
    # https://packaging.python.org/specifications/platform-compatibility-tags/
    # PEP 600
    LEGACY_ALIASES = {
        "manylinux1_x86_64": "manylinux_2_5_x86_64",
        "manylinux1_i686": "manylinux_2_5_i686",
        "manylinux2010_x86_64": "manylinux_2_12_x86_64",
        "manylinux2010_i686": "manylinux_2_12_i686",
        "manylinux2014_x86_64": "manylinux_2_17_x86_64",
        "manylinux2014_i686": "manylinux_2_17_i686",
        "manylinux2014_aarch64": "manylinux_2_17_aarch64",
        "manylinux2014_armv7l": "manylinux_2_17_armv7l",
        "manylinux2014_ppc64": "manylinux_2_17_ppc64",
        "manylinux2014_ppc64le": "manylinux_2_17_ppc64le",
        "manylinux2014_s390x": "manylinux_2_17_s390x",
    }


    interpreter_tag = tags[0]
    platform_tag = tags[-1]

    if not (interpreter_tag[:2] == 'py' or interpreter_tag[:2] == 'cp'):
        # Not a cpython or generic python package
        raise Exception

    if platform_tag == "any":
        return True

    if 'win32' in platform_tag:
        return False

    elif 'macosx' in platform_tag:
        return False

    else:
        # linux tag
        # Directly from PEP 600
        # Normalize and parse the tag
        tag = LEGACY_ALIASES.get(platform_tag, platform_tag)
        m = re.match("manylinux_([0-9]+)_([0-9]+)_(.*)", tag)
        if not m:
            return False
        tag_major_str, tag_minor_str, tag_arch = m.groups()
        tag_major = int(tag_major_str)
        tag_minor = int(tag_minor_str)


        if not tag_arch == DEPLOYMENT_PLATFORM:
            return False

        return True

    


for project_obj in pkg_resources.working_set:
    # For information on this object check 
    # https://setuptools.pypa.io/en/latest/pkg_resources.html#distribution-objects
    # Distribution Object

    # find the dist info directory that will contain metadata about the package
    dist_dir_location =  os.path.join(project_obj.location, f"{project_obj.project_name.replace('-', '_')}-{project_obj.parsed_version}.dist-info")
    toplevel_file_location  = os.path.join(dist_dir_location, 'top_level.txt')
    wheel_info = os.path.join(dist_dir_location, "WHEEL")
    
    if not os.path.isdir(dist_dir_location):
        continue

    if not os.path.isfile(toplevel_file_location):
        # If not top level file is present, then assume the only top level module available is the project name
        MOD_NAME_TO_PRJ_OBJ[project_obj.project_name] = project_obj
        PRJ_NAME_TO_TOP_LEVEL_MODULES[project_obj.project_name] = [project_obj.project_name]
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
            potential_file = os.path.join(project_obj.location, potential_module+".py")

            if not os.path.isdir(potential_dir) and not os.path.isfile(potential_file):
                #print(f"Could not find module {potential_module} at {dist_dir_location}")
                continue

            actual_modules.append(potential_module)

        PRJ_NAME_TO_TOP_LEVEL_MODULES[project_obj.project_name] = actual_modules


    with open(wheel_info) as fh:
        lines = fh.readlines()

        # https://www.python.org/dev/peps/pep-0425/
        # if it is not pure it should only have one tag 
        # We are going ot check the tags of the package to make sure it is compatible with the target deployment platform
        tags = [x.split(":")[1] for x in lines if x.split(":")[0]=='Tag'][0].strip().split("-")
        
        if not is_platform_compatible(tags):
            INCOMPATIBLE_PROJECTS.add(project_obj.project_name)



def get_module_info(pkg_name) -> ModulePackagingInfo:

    # TODO add another cache here
    info = create_module_package_info(pkg_name)
   

    return info


def create_module_package_info(identifier: str) -> ModulePackagingInfo:
    """
    Create the information needed to package this dependency with a parsed function. We use the recursive method because
    we must compute the package information for the dependencies of this dependency. Returns a ModulePackagingInfo objects
    that represent the information to handle the packaging steps. 

    Args:
        identifier (str): This can be either the package or project name 

    Returns
        information (List[ModulePackagingInfo]): information for the packages to package

    """    
    pkg_info =  _recursive_create_module_package_info(identifier)

    return pkg_info


def _recursive_create_module_package_info(pkg_name: str) -> ModulePackagingInfo:

    if pkg_name in PACKAGE_CACHE:
        #print(f"CACHE HIT -> {pkg_name}")
        return PACKAGE_CACHE.get(pkg_name)
        

    
    if not pkg_name in sys.modules and not pkg_name in MOD_NAME_TO_PRJ_OBJ and not pkg_name in DIFF_PROJECT_TO_TOP:
        print(f"BAD PKG NAME -> {pkg_name}")
        raise Exception

    else:
        standard_lib_info = _load_standard_library_information("3_6")
        aws_packages = _load_aws_packages("3_6")
        pip_packages = _load_mod_to_prj()


        if pkg_name in standard_lib_info:
            rv = ModulePackagingInfo(**{
                "pkg_name": pkg_name,
                "type":  PackageTypes.STANDARDLIB,
                "version_id": None,
                "fp": None
            })

        elif pkg_name in aws_packages:
            rv = ModulePackagingInfo(**{
                "pkg_name": pkg_name,
                "type":  PackageTypes.AWSINCLUDED,
                "version_id": None,
                "fp": None
            })

        elif pkg_name in pip_packages:
            tmp_distribution_obj = pip_packages.get(pkg_name)
    
            project_name = tmp_distribution_obj.project_name

            if project_name in INCOMPATIBLE_PROJECTS:
                if CDEV_SETTINGS.get("PULL_INCOMPATIBLE_LIBRARIES"):
                    if docker_package_builder.docker_available():
                        print(f"DOWNLOADING {tmp_distribution_obj.project_name} for oackage {pkg_name}")
                        rv = docker_package_builder.download_package(tmp_distribution_obj, lambda_python_environments.py38_arm64, pkg_name)
                        PACKAGE_CACHE[pkg_name] = rv
                        return rv

                    else:
                        raise Exception


                raise Exception

            # The package could be either a folder (normal case) or a single python file (ex: 'six' package)
            # If it can not be found as either than there is an issue
            potential_dir = os.path.join(pip_packages.get(pkg_name).location, pkg_name)
            potential_file = os.path.join(pip_packages.get(pkg_name).location, pkg_name+".py")
           

            if os.path.isdir(potential_dir):
                tmp_fp = potential_dir

            elif os.path.isfile(potential_file):
                tmp_fp = potential_file
            else:
                raise Exception

            # required modules from this package
            tmp_dependencies_flat = _recursive_check_for_dependencies_project(tmp_distribution_obj)

            rv = ModulePackagingInfo(**{
                "pkg_name": pkg_name,
                "type":  PackageTypes.PIP,
                "version_id": tmp_distribution_obj.version,
                "fp": tmp_fp
            })
        
            
            rv.set_flat(tmp_dependencies_flat)

        else:
            mod = sys.modules.get(pkg_name)
            if mod:
                if not mod.__file__:
                    tmp_type = PackageTypes.BUILTIN
                    tmp_fp = None
                    tmp_version = None
                else:
                    tmp_type = PackageTypes.LOCALPACKAGE
                    tmp_version = None

                    if mod.__file__.split("/")[-1] == "__init__.py":
                        tmp_fp = os.path.dirname(mod.__file__)
                    else:
                        tmp_fp = mod.__file__
            else:
                print("BAADDD")
                raise Exception

        
            rv = ModulePackagingInfo(**{
                "pkg_name": pkg_name,
                "type":  tmp_type,
                "version_id": tmp_version,
                "fp": tmp_fp
            })
        
            dependencies_flat = _recursive_check_for_dependencies_package(rv)
            rv.set_flat(dependencies_flat)

        
        PACKAGE_CACHE[pkg_name] = rv
        return rv


def _recursive_check_for_dependencies_project(project_distribution_obj: pkg_resources.Distribution) -> List[ModulePackagingInfo]:
    """
    Create the ModulePackagingInfo objects for all the top level modules in this package. 
    """
    tmp_flat = set()

    
    for project_obj in project_distribution_obj.requires():

        if project_obj.project_name in PRJ_NAME_TO_TOP_LEVEL_MODULES:
            project_name = project_obj.project_name

        elif project_obj.project_name in MOD_NAME_TO_PRJ_OBJ:
            project_name = MOD_NAME_TO_PRJ_OBJ.get(project_obj.project_name).project_name

        else:
            raise Exception



        top_level_modules = PRJ_NAME_TO_TOP_LEVEL_MODULES.get(project_name)


        for req in top_level_modules:
            tmp_dep = _recursive_create_module_package_info(req)
            tmp_flat.add(tmp_dep)
            if tmp_dep.flat:
                tmp_flat = tmp_flat.union( set(tmp_dep.flat) )


    return tmp_flat


def _recursive_check_for_dependencies_package(pkg: ModulePackagingInfo) -> List[ModulePackagingInfo]:        
    tmp_flat = set()
    

    required_items = _get_local_package_dependencies(pkg)
    

    for req in required_items:
        tmp_dep = _recursive_create_module_package_info(req)

        tmp_flat.add(tmp_dep)

        if tmp_dep.flat:
            tmp_flat = tmp_flat.union(set(tmp_dep.flat))

    return list(tmp_flat)


    
def _get_local_package_dependencies(pkg: ModulePackagingInfo) -> List[str]:
    # This is the hardest case of dependencies to handle
    # This is if the developer imports a local python module they created or got without pip
    # This module can depend on other packages (local,pip,etc)
    # The only way to get this dependency tree is to parse each file for import statements :upsidedownsmile: 

    _current_working_dir = CDEV_SETTINGS.get("CURRENT_PARSING_DIR")

    if not _current_working_dir:
        # This setting should be set
        raise Exception

    if os.path.isdir(pkg.fp):
        if pkg.fp == _current_working_dir:
            print(f'can not include whole current directory -> {pkg.fp}')
            raise Exception
        elif is_parent_dir(pkg.fp, _current_working_dir):
            print(f'can not include entire parent directory -> {pkg.fp}')
            raise Exception
        else:
            print(f'check only this file -> {pkg.fp}')
            pkg_names = cdev_parser.parse_folder_for_dependencies(pkg.fp)

    else:
        pkg_dir = os.path.dirname(pkg.fp)

        if pkg_dir == _current_working_dir:
            print(f'check only this file -> {pkg.fp}')
            pkg_names = []
        elif is_parent_dir(pkg.fp, _current_working_dir):
            print(f'can not include entire parent directory -> {pkg_dir}')
            raise Exception
        else:
            print(f"Not same {pkg_dir} ; {_current_working_dir}")
            pkg_names = cdev_parser.parse_folder_for_dependencies(pkg.fp)

    return list(pkg_names)



def _load_standard_library_information(version="3_6"):
    FILE_LOC = os.path.join(os.path.dirname(__file__), "standard_library_names", f"python_{version}")

    if not os.path.isfile(FILE_LOC):
        # TODO throw error
        raise FileNotFoundError
        
    with open(FILE_LOC) as fh:
        return set(fh.read().splitlines())


def _load_aws_packages(version="3_6"):
    return set(["boto3", "botocore"])


def _load_mod_to_prj():
    return MOD_NAME_TO_PRJ_OBJ


def is_parent_dir(parent, child) -> bool:
    # Smooth out relative path names, note: if you are concerned about symbolic links, you should use os.path.realpath too
    parent_path = os.path.abspath(parent)
    child_path = os.path.abspath(child)

    # Compare the common path of the parent and child path with the common path of just the parent path. Using the commonpath method on just the parent path will regularise the path name in the same way as the comparison that deals with both paths, removing any trailing path separator
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])
    
