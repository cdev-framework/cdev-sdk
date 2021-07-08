import os
from posixpath import split
from sys import version_info
from typing import List

from cdev.settings import SETTINGS as cdev_settings
from cdev.utils import paths as cdev_paths

BASE_FILES_PATH = cdev_settings.get("CDEV_INTERMEDIATE_FILES_LOCATION")

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
    split_path[-1] = split_path[-1].split(".")[0] + "_py"
    try:
        split_path.remove(".")
        split_path.remove("..")
    except Exception as e:
        pass

    if prefix:
        split_path.insert(0, prefix)

    final_file_dir = _create_path(BASE_FILES_PATH, split_path)

    return os.path.join(final_file_dir,function_name+".py")


def _create_path(startingpath, fullpath):
    # This functions takes a starting path and list of child dir and makes them all
    # Returns the final path

    # ex: _create_path(""./basedir", ["sub1", "sub2"])
    # creates: 
    #   - ./basedir/sub1/
    #   - ./basedir/sub1/sub2

    if not os.path.isdir(startingpath):
        return None

    intermediate_path = startingpath

    for p in fullpath:
        if not os.path.isdir(os.path.join(intermediate_path, p)):
            os.mkdir(os.path.join(intermediate_path, p))

        intermediate_path = os.path.join(intermediate_path, p)

    return intermediate_path
