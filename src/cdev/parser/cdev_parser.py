import os

import parser.parser_objects
import parser.parser_utils as p_utils

## This file has the highest level functions for use by other modules. Only this file will expose functionality to other modules.


def parse_functions_from_file(file_loc, include_functions=[]):

    if not os.path.isfile(file_loc):
        raise FileNotFoundError(f"cdev_parser: could not find file at -> {file_loc}")

    file_source_code = ""

    with open(file_loc, 'r') as fh:
        file_source_code = fh.read()

    file_globals = p_utils.get_global_module_symbols(file_source_code, file_loc)

    return "Y"








