import os
from sys import version_info
from typing import List, Set

from pydantic.types import FilePath

from cdev.settings import SETTINGS as cdev_settings
from cdev.utils import paths as cdev_paths, hasher as cdev_hasher

INTERMEDIATE_FOLDER = cdev_settings.get("CDEV_INTERMEDIATE_FOLDER_LOCATION")

def get_lines_from_file_list(file_list, function_info) -> List[str]:
    # Get the list of lines from a file based on the function info provided
    line_nos = _compress_lines(function_info)

    actual_lines = []

    for i in line_nos:
        if i == -1:
            actual_lines.append(os.linesep)
        elif i <= len(file_list):
            actual_lines.append(file_list[i-1])

    return actual_lines


def get_file_as_list(path):
    # Returns the file as a list of lines
    if not os.path.isfile:
        return None

    with open(path) as fh:
        rv = fh.read().splitlines()

    return rv


def _compress_lines(original_lines):
    # Takes input SORTED([(l1,l2), (l3,l4), ...])
    # returns [l1,...,l2,l3,...,l4]
    rv = []

    for pair in original_lines:
        for i in range(pair[0], pair[1]+1):
            if rv and rv[-1] == i:
                # if the last element already equals the current value continue... helps eleminate touching boundaries
                continue

            rv.append(i)

        if version_info > (3,8):
            rv.append(-1)

    return rv 


def get_parsed_path(original_path, function_name, prefix=None):
    split_path = cdev_paths.get_relative_to_project_path(original_path).split("/")
    # the last item in the path is .py file name... change the  .py to _py so it works as a dir
    final_file_name =  split_path[-1].split(".")[0] + "_" + function_name+".py"
    try:
        split_path.remove(".")
        split_path.remove("..")
    except Exception as e:
        pass

    if prefix:
        split_path.insert(0, prefix)

    
    final_file_dir = cdev_paths.create_path(INTERMEDIATE_FOLDER, split_path[:-1])

    return os.path.join(final_file_dir, final_file_name)


class PackageTypes:
    BUILTIN = "builtin"
    STANDARDLIB = "standardlib"
    PIP = "pip"
    LOCALPACKAGE = "localpackage"
    AWSINCLUDED = "awsincluded"


class PackageInfo:
    def __init__(self, pkg_name: str, type: PackageTypes, version_id: str=None , fp: FilePath=None ) -> None:
        self.pkg_name = pkg_name
        self.type = type
        self.version_id = version_id
        self.fp = fp
        self.tree = None
        self.flat = None


    def set_tree(self, tree: List):
        self.tree = tree

    
    def set_flat(self, flat: Set['PackageInfo']):
        self.flat = flat


    def get_id_str(self) -> str:
        if self.type == PackageTypes.LOCALPACKAGE:
            if os.path.isfile(self.fp):
                return f"{self.pkg_name}-{self.fp}-{cdev_hasher.hash_file(self.fp)}"

            else:
                return f"{self.pkg_name}-{self.fp}"

        elif self.type == PackageTypes.PIP:
            return f"{self.pkg_name}-{self.version_id}"

        else:
            return self.pkg_name

    def __str__(self) -> str:
        return self.get_id_str()


    def __hash__(self) -> int:
        return int(cdev_hasher.hash_string(self.get_id_str()), base=16)
