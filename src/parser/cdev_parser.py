import os

from src.parser.parser_objects import *
import src.parser.parser_utils as p_utils
from src.parser.cdev_parser_exceptions import *

## This file has the highest level functions for use by other modules. Only this file will expose functionality to other modules.


def parse_functions_from_file(file_loc, include_functions=[]):

    try:
        file_information = p_utils.get_file_information(file_loc, include_functions)
    except CouldNotParseFileError as e:
        print(e)

    return "Y"
