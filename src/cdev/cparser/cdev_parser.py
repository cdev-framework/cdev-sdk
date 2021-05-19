import os

from cdev.cparser.parser_objects import *
import cdev.cparser.parser_utils as p_utils
from cdev.cparser.cdev_parser_exceptions import *

## This file has the highest level functions for use by other modules. Only this file will expose functionality to other modules.


def parse_functions_from_file(file_loc, include_functions=[], function_manual_includes={}, global_manual_includes=[]):

    try:
        file_information = p_utils.get_file_information(
            file_loc, include_functions, function_manual_includes, global_manual_includes)
    except InvalidDataError as e:
        file_information = None
        print(f"{type(e)} -> {e.message}")
    except CouldNotParseFileError as e:
        file_information = None
        print(f"{type(e.error)} -> {e.error.message}")

    return file_information
