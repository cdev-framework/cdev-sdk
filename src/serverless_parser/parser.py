from pydantic.types import DirectoryPath

from .parser_objects import *
from . import parser_utils as p_utils
from .parser_exceptions import *


## This file has the highest level functions for use by other modules. Only this file will expose functionality to other modules.


def parse_functions_from_file(
    file_loc,
    include_functions=[],
    function_manual_includes={},
    global_manual_includes=[],
    remove_top_annotation=False,
) -> file_information:
    try:
        file_information = p_utils.get_file_information(
            file_loc,
            include_functions,
            function_manual_includes,
            global_manual_includes,
            remove_top_annotation,
        )
    except InvalidDataError as e:
        file_information = None
        print(f"{type(e)} -> {e.message}")
    except CouldNotParseFileError as e:
        file_information = None
        print(f"{type(e.error)} -> {e.error.message}")

    return file_information


def parse_file_for_dependencies(file_loc: DirectoryPath):
    return p_utils.get_file_imported_symbols(file_loc)
