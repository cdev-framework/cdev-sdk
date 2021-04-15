import os

from src.parser.parser_objects import *
import src.parser.parser_utils as p_utils
from src.parser.cdev_parser_exceptions import *

## This file has the highest level functions for use by other modules. Only this file will expose functionality to other modules.


def parse_functions_from_file(file_loc, include_functions=[]):

    if not os.path.isfile(file_loc):
        raise FileNotFoundError(
            f"cdev_parser: could not find file at -> {file_loc}")

    file_obj = file_information(file_loc)

    try:
        file_globals = p_utils.get_global_information(file_obj)
    except CouldNotParseFileError as e:
        print(e)

    return "Y"
