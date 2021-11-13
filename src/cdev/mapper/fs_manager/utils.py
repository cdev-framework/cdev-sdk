import os
from sys import version_info
from typing import List, Optional, Set

from pydantic.types import FilePath
from pydantic import BaseModel
from enum import Enum
from pathlib import PosixPath, WindowsPath

from cdev.settings import SETTINGS as cdev_settings
from cdev.utils import paths as cdev_paths, hasher as cdev_hasher

from rich import print

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



class ExternalDependencyWriteInfo(BaseModel):
    location: str
    id: str

    class Config:
        json_encoders = {
            PosixPath: lambda v: v.as_posix(), # or lambda v: str(v)
            WindowsPath: lambda v: v.as_posix()
        }

        extra='ignore'


class LocalDependencyArchiveInfo(BaseModel):
    name: str
    artifact_path: FilePath
    hash: str

class PackageTypes(str, Enum):
    BUILTIN = "builtin"
    STANDARDLIB = "standardlib"
    PIP = "pip"
    LOCALPACKAGE = "localpackage"
    AWSINCLUDED = "awsincluded"


class ModulePackagingInfo(BaseModel):
    module_name: str
    type: PackageTypes
    version_id: Optional[str]
    fp: Optional[str]
    tree: Optional[List['ModulePackagingInfo']]
    flat: Optional[List['ModulePackagingInfo']]
    is_relative: Optional[bool]

    def set_flat(self, flat: List['ModulePackagingInfo']):
        self.flat = flat

    def set_tree(self, tree: List['ModulePackagingInfo']):
        self.tree = tree

    def get_id_str(self) -> str:
        if self.type == PackageTypes.LOCALPACKAGE:
            if os.path.isfile(self.fp):
                return f"{self.module_name}-{self.fp}-{cdev_hasher.hash_file(self.fp)}"

            else:
                return f"{self.module_name}-{self.fp}"

        elif self.type == PackageTypes.PIP:
            return f"{self.module_name}-{self.version_id}"

        else:
            return self.module_name

    def __str__(self) -> str:
        return self.get_id_str()

    def __repr__(self) -> str:
        return f"{self.get_id_str()}"


    def __hash__(self) -> int:
        return int(cdev_hasher.hash_string(self.get_id_str()), base=16)

ModulePackagingInfo.update_forward_refs()


_depth_to_color  = {
    0: "white",
    1: "blue",
    2: "yellow",
    3: "magenta",
    4: "red"
}


def print_dependency_tree(handler_name: str, top_level_modules: List[ModulePackagingInfo]):
    print(f"Handler: {handler_name}")

    for module_info in top_level_modules:
        
        _recursive_dfs_print(module_info, 0)
        print("|")



def _recursive_dfs_print(module_info: ModulePackagingInfo, depth: int):
    
    base_str = f"|[{_depth_to_color.get(depth%5)}]{'-' * depth } {module_info.module_name}[/{_depth_to_color.get(depth%5)}] ({module_info.type})"   
    print(base_str)

    if module_info.tree:
        for child_module in module_info.tree:
            _recursive_dfs_print(child_module, depth+1)


def print_handler_package():
    pass


def print_layer_package():
    pass



class lambda_python_environments(str, Enum):
    py36 = "py36"
    py37 = "py37"
    py38_x86_64 = "py38-x86_64"
    py38_arm64 = "py38-arm64"
    py39_x86_64 = " py39-x86_64"
    py39_arm64 = "py39-arm64"
    py3_x86_64 = "py3-x86_64"
    py3_arm64 = "py3-arm64"


CONTAINER_NAMES = {
    lambda_python_environments.py36: "public.ecr.aws/lambda/python:3.6",
    lambda_python_environments.py37: "public.ecr.aws/lambda/python:3.7",
    lambda_python_environments.py38_x86_64: "public.ecr.aws/lambda/python:3.8-x86_64",
    lambda_python_environments.py38_arm64: "public.ecr.aws/lambda/python:3.8-arm64",
    lambda_python_environments.py39_x86_64: "public.ecr.aws/lambda/python:3.9-x86_64",
    lambda_python_environments.py39_arm64: "public.ecr.aws/lambda/python:3.9-arm64",
    lambda_python_environments.py3_x86_64: "public.ecr.aws/lambda/python:3-x86_64",
    lambda_python_environments.py3_arm64: "public.ecr.aws/lambda/python:3-arm64",   
}
