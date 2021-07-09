import os
import hashlib

from sortedcontainers import SortedList

from .parser_objects import *
from .import parser_utils as p_utils
from .cdev_parser_exceptions import *

from ..fs_manager.package_mananger import get_package_info



## This file has the highest level functions for use by other modules. Only this file will expose functionality to other modules.


def parse_functions_from_file(file_loc, include_functions=[], function_manual_includes={}, global_manual_includes=[], remove_top_annotation=False):
    try:
        file_information = p_utils.get_file_information(
            file_loc, include_functions, function_manual_includes, global_manual_includes, remove_top_annotation)
    except InvalidDataError as e:
        file_information = None
        print(f"{type(e)} -> {e.message}")
    except CouldNotParseFileError as e:
        file_information = None
        print(f"{type(e.error)} -> {e.error.message}")

    for parsed_function in file_information.parsed_functions:
        ALL_PACKAGES = set()
        if parsed_function.imported_packages:
            for pkg_name in parsed_function.imported_packages:
                ALL_PACKAGES = ALL_PACKAGES.union(get_package_info(pkg_name))

        parsed_function.needed_packages = ALL_PACKAGES

        if ALL_PACKAGES:
            sorted_packages =  SortedList(ALL_PACKAGES)
            parsed_function.needed_imports = sorted_packages

    return file_information


def parse_folder_for_dependencies(folder_loc):
    return p_utils.get_folders_imported_symbols(folder_loc)
