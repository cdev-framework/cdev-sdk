import os
import sys
import pkg_resources
from zipfile import ZipFile
from typing import List
import re


from cdev.settings import SETTINGS as CDEV_SETTINGS
from ..cparser import cdev_parser 

from packaging.utils import canonicalize_name
from sysconfig import get_platform

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
PKG_NAME_TO_PIP_PKG = {}

DIFF_PROJECT_TO_TOP = {}

DEPLOYMENT_PLATFORM = "x86_64"

INCOMPATIBLE_LIBRARIES = set()

def is_platform_compatible(tags: List[str]) -> bool:
    # https://packaging.python.org/specifications/platform-compatibility-tags/
    # PEP 425
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

    


for f in pkg_resources.working_set:
    #find the dist info directory that will contain metadata about the package
    dist_dir_location =  os.path.join(f.location, f"{f.project_name.replace('-', '_')}-{f.parsed_version}.dist-info")
    toplevel_file_location  = os.path.join(dist_dir_location, 'top_level.txt')
    wheel_info = os.path.join(dist_dir_location, "WHEEL")
    
    if not os.path.isdir(dist_dir_location):
        continue

    if not os.path.isfile(toplevel_file_location):
        PKG_NAME_TO_PIP_PKG[f.project_name] = f
        continue

    #print(f"{f} -> {f.platform}")
    with open(toplevel_file_location) as fh:
        pkg_python_name = fh.readline().strip()
        PKG_NAME_TO_PIP_PKG[pkg_python_name] = f

        if not pkg_python_name == f.project_name:
            DIFF_PROJECT_TO_TOP[f.project_name] = pkg_python_name

    with open(wheel_info) as fh:
        lines = fh.readlines()

        # https://www.python.org/dev/peps/pep-0425/
        # if it is not pure it should only have one tag 
        # We are going ot check the tags of the package to make sure it is compatible with the target deployment platform
        tags = [x.split(":")[1] for x in lines if x.split(":")[0]=='Tag'][0].strip().split("-")
        
        if not is_platform_compatible(tags):
            INCOMPATIBLE_LIBRARIES.add(pkg_python_name)



class PackageTypes:
    BUILTIN = "builtin"
    STANDARDLIB = "standardlib"
    PIP = "pip"
    LOCALPACKAGE = "localpackage"
    AWSINCLUDED = "awsincluded"


def get_all_package_info(pkg_names): 
    # Take in a list/set of all top level pkgs a function uses and return the set of ALL pkgs that are needed for its layers
    rv = set()

    for pkg_name in pkg_names:
        rv = rv.union(get_package_info(pkg_name))

    return sorted(rv)


def get_package_info(pkg_name):

    info = create_package_info(pkg_name)
    
    if info.get("flat"):
        return {info.get("pkg_name"): info}

    return {}


def create_package_info(pkg_name):
    # RV :  {
    #   pkg_name: pkg_name,
    #   type: ENUM("builtin", "standardlib", "pip", "localpackage", "awsincluded")
    #   ?Dependencies: SET({<objs>}),
    #   ?AsList: [{objs}],
    #   ?fp: path_to_dir
    # }
    pkg_info =  _recursive_create_package_info(pkg_name)
    #print(pkg_info)
    return pkg_info


def create_zip_archive(pkgs, layername):
    
    BASE_LOCATION = os.path.join(CDEV_SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "layers")

    zip_file_location = os.path.join(BASE_LOCATION,"layer_"+layername+".zip")

    with ZipFile(zip_file_location, 'w') as zipfile:
        for pkg in pkgs:
            pkg_info = PACKAGE_CACHE.get(pkg)
            
            if not pkg_info:
                print("CANT FIND INFORMATION")

            for dirname, subdirs, files in os.walk(pkg_info.get("fp")):
                zip_dir_name = os.path.normpath( os.path.join('python', pkg ,os.path.relpath(dirname ,pkg_info.get('fp') )) )

                for filename in files:
                    zipfile.write(os.path.join(dirname, filename), os.path.join(zip_dir_name, filename))

    return zip_file_location


def _recursive_create_package_info(unmodified_pkg_name):

    if unmodified_pkg_name in PACKAGE_CACHE:
        #print(f"CACHE HIT -> {pkg_name}")
        return PACKAGE_CACHE.get(unmodified_pkg_name)
        

    rv =  {"pkg_name": unmodified_pkg_name}
    if not unmodified_pkg_name in sys.modules and not unmodified_pkg_name in PKG_NAME_TO_PIP_PKG and not unmodified_pkg_name in DIFF_PROJECT_TO_TOP:
        print(f"BAD PKG NAME -> {unmodified_pkg_name}")
        raise Exception

    else:
        standard_lib_info = _load_standard_library_information("3_6")
        aws_packages = _load_aws_packages("3_6")
        pip_packages = _load_pip_packages()

        pkg_name = DIFF_PROJECT_TO_TOP.get(unmodified_pkg_name, unmodified_pkg_name)
        
        if pkg_name in INCOMPATIBLE_LIBRARIES:
            raise Exception


        mod = sys.modules.get(pkg_name)
        

        if pkg_name in standard_lib_info:
            rv["type"] = PackageTypes.STANDARDLIB 

        elif pkg_name in aws_packages:
            rv["type"] = PackageTypes.AWSINCLUDED

        elif pkg_name in pip_packages:
            rv["type"] = PackageTypes.PIP
            # The package could be either a folder (normal case) or a single python file (ex: 'six' package)
            # If it can not be found as either than there is an issue
            potential_dir = os.path.join(pip_packages.get(pkg_name).location, pkg_name)
            potential_file = os.path.join(pip_packages.get(pkg_name).location, pkg_name+".py") 

            if os.path.isdir(potential_dir):
                rv["fp"] = potential_dir

            elif os.path.isfile( potential_file):
                rv["fp"] = potential_file

            else:
                raise Exception

        else:
            if mod:
                if not mod.__file__:
                    rv["type"] = PackageTypes.BUILTIN
                else:
                    rv["type"] = PackageTypes.LOCALPACKAGE

                    if mod.__file__.split("/")[-1] == "__init__.py":
                        rv["fp"] = os.path.dirname(mod.__file__)
                    else:
                        rv["fp"] = mod.__file__
            else:
                print("BAADDD")
                raise Exception
        
        dependencies = _recursive_check_for_dependencies(rv)

        rv["tree"] = dependencies.get("tree")
        rv["flat"] = dependencies.get("flat")

        PACKAGE_CACHE[pkg_name] = rv

        return rv


def _recursive_check_for_dependencies(obj):

    if obj.get("type") == PackageTypes.BUILTIN or obj.get("type") == PackageTypes.STANDARDLIB or obj.get("type") == PackageTypes.AWSINCLUDED:
        return obj

    if obj.get("type") == PackageTypes.PIP:
        
        if obj.get("pkg_name") in DIFF_PROJECT_TO_TOP:
            # package linked by pip project name that is different than the top level name of the module
            old_name = obj.get("pkg_name")
            pkg_name = DIFF_PROJECT_TO_TOP.get(obj.get("pkg_name"))
            
        else:
            pkg_name = obj.get("pkg_name")


        item = PKG_NAME_TO_PIP_PKG.get(pkg_name)

        rv = {}
        rv['flat'] = set([(pkg_name, obj.get("type"), obj.get("fp") )])
        rv['tree'] = []

        for req in item.requires():
            tmp = _recursive_create_package_info(req.key)

            rv["tree"].append(tmp)
            if tmp.get("flat"):
                rv['flat'] = rv["flat"].union(tmp.get("flat"))

        return rv

    if obj.get("type") == PackageTypes.LOCALPACKAGE:
        items = _get_local_package_dependencies(obj)
        
        rv = {}
        rv['flat'] = set([(obj.get('pkg_name'), obj.get("type"), obj.get("fp") )])
        rv['tree'] = []

        for req in items:
            tmp = _recursive_create_package_info(req)

            rv["tree"].append(tmp)
            if tmp.get("flat"):
                rv['flat'] = rv["flat"].union(tmp.get("flat"))

        return rv

    return obj


    
def _get_local_package_dependencies(pkg):
    # This is the hardest case of dependencies to handle
    # This is if the developer imports a local python module they created or got without pip
    # This module can depend on other packages (local,pip,etc)
    # The only way to get this dependency tree is to parse each file for import statements :upsidedownsmile: 

    _current_working_dir = CDEV_SETTINGS.get("CURRENT_PARSING_DIR")

    if not _current_working_dir:
        # This setting should be set
        raise Exception

    if os.path.isdir(pkg.get("fp")):
        if pkg.get("fp") == _current_working_dir:
            print(f'can not include whole current directory -> {pkg.get("fp")}')
            raise Exception
        elif is_parent_dir(pkg.get("fp"), _current_working_dir):
            print(f'can not include entire parent directory -> {pkg.get("fp")}')
            raise Exception
        else:
            print(f'check only this file -> {pkg.get("fp")}')
            pkg_names = cdev_parser.parse_folder_for_dependencies(pkg.get("fp"))

    else:
        pkg_dir = os.path.dirname(pkg.get("fp"))

        if pkg_dir == _current_working_dir:
            print(f'check only this file -> {pkg.get("fp")}')
            pkg_names = []
        elif is_parent_dir(pkg.get("fp"), _current_working_dir):
            print(f'can not include entire parent directory -> {pkg_dir}')
            raise Exception
        else:
            print(f"Not same {pkg_dir} ; {_current_working_dir}")
            pkg_names = cdev_parser.parse_folder_for_dependencies(pkg.get("fp"))

    return pkg_names



def _load_standard_library_information(version="3_6"):
    FILE_LOC = os.path.join(os.path.dirname(__file__), "standard_library_names", f"python_{version}")

    if not os.path.isfile(FILE_LOC):
        # TODO throw error
        raise FileNotFoundError
        
    with open(FILE_LOC) as fh:
        return set(fh.read().splitlines())


def _load_aws_packages(version="3_6"):
    return set(["boto3", "botocore"])


def _load_pip_packages():
    return PKG_NAME_TO_PIP_PKG


def is_parent_dir(parent, child) -> bool:
    # Smooth out relative path names, note: if you are concerned about symbolic links, you should use os.path.realpath too
    parent_path = os.path.abspath(parent)
    child_path = os.path.abspath(child)

    # Compare the common path of the parent and child path with the common path of just the parent path. Using the commonpath method on just the parent path will regularise the path name in the same way as the comparison that deals with both paths, removing any trailing path separator
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])
    
