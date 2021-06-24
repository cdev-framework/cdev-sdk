from ast import parse
import os

from . import utils as fs_utils


def write_intermediate_file(original_path, needed_lines, parsed_path):
    # Function takes an original file path and a file_info obj that describes what lines need to be parsed 
    # from the original file

    # Prefix is a variable that will be added to the path after the BASE PATH but before the split path

    # original_path: path to file
    # function_info: [{"function_name": str, "needed_lines": []}]
    # print(f"FROM {original_path} WRITE {function_info.get('needed_lines')} TO {parsed_path}")

    if not os.path.isfile(original_path):
        print(f"nah {original_path}")
        return False


    file_list =  fs_utils.get_file_as_list(original_path)
    

    actual_lines = fs_utils.get_lines_from_file_list(file_list, needed_lines)
    _write_intermediate_function(parsed_path, actual_lines)

    return True

def _write_intermediate_function(path, lines):
    # Function takes a filepath (fp), filename, and lines then writes the lines to the file
    # This function is used to create the intermediate file
    # It creates the file on the file system and also returns metadata about the file


    with open(path, "w") as fh:
        for line in lines:
            fh.write(line)
            fh.write("\n")

    return True



