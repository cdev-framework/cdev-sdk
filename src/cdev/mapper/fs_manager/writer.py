from typing import List
from ast import parse
import os

from pydantic.types import FilePath

from . import utils as fs_utils
from zipfile import ZipFile


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

    cleaned_actual_lines = _clean_lines(actual_lines)
    print(f"cleand line -> {cleaned_actual_lines}")
    _write_intermediate_function(parsed_path, cleaned_actual_lines)
    _make_intermediate_zip(parsed_path)

    return True


def _clean_lines(lines: List[str]):
    """
    Parsed functions can have empty lines or comments as the last lines of the, so we are going to start from the end of the file and remove those lines
    """

    # final line should be an offset from the end of the list the represents the final real line of python code
    final_line_no = -1


    for i in range(len(lines)-1):
        tmp_line = lines[-(i+1)]

        # if the line is blank it is not a valid line
        if not tmp_line:
            continue

        # if the line is a comment (starts with '#') or is just whitespace
        if not(tmp_line[0] == '#' or tmp_line.isspace()):
            final_line_no = i
            break
        
    if final_line_no == -1 or final_line_no == 0:
        rv = lines
    else:
        rv = lines[:-final_line_no]
    
    return rv


def _write_intermediate_function(path, lines):
    # Function takes a filepath (fp), filename, and lines then writes the lines to the file
    # This function is used to create the intermediate file
    # It creates the file on the file system and also returns metadata about the file

    # TODO (Medium) Add Formatting settings from Cdev Settings
    #_strip_new_lines_from_source_lines(lines)

    with open(path, "w") as fh:
        for line in lines:
            fh.write(line)
            fh.write("\n")

    return True

def _make_intermediate_zip(path: str):
    filename = os.path.split(path)[1]
    zip_archive_location = os.path.join(os.path.dirname(path), filename[:-3] + ".zip")

    with ZipFile(zip_archive_location, 'w') as zipfile:
        zipfile.write(path, filename)

