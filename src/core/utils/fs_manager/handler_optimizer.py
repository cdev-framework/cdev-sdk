import os
from pydantic import DirectoryPath, FilePath
from typing import List, Set, Tuple, Union, Any
import sys
from pathlib import Path

from . import writer

from core.utils.operations import concatenate
from core.utils.paths import create_path_from_workspace


def create_optimized_handler_artifact(
    original_file_location: FilePath,
    additional_files: List[Union[FilePath, DirectoryPath]],
    base_packaging_path: DirectoryPath,
    intermediate_path: DirectoryPath,
    needed_lines: List[int],
    suffix: str = "",
    excludes: Set[str] = set(),
) -> Tuple[FilePath, str]:
    """Create the handler archive and hash based on the given information.

    Args:
        original_file_location (FilePath): location of file
        base_packaging_path (DirectoryPath): directory to write artifact
        intermediate_path (DirectoryPath): intermediate path for parsed functions
        needed_lines (List[int]): lines needed for the handler file
        additional_files (List[Union[FilePath, DirectoryPath]], optional): additional files for the artifact. Defaults to [].
        suffix (str, optional): suffix for final artifact. Defaults to "".
        excludes (Set[str], optional): folders to exclude from the artifact. Defaults to set().

    Returns:
        Tuple[FilePath,str]: Tuple of archive filepath and hash
    """
    # Make sure the path exists
    create_path_from_workspace(base_packaging_path)

    relative_handler_path = _get_relative_path(
        original_file_location, base_packaging_path
    )

    handler_intermediate_tmp = os.path.join(intermediate_path, relative_handler_path)
    handler_intermediate_final = (
        handler_intermediate_tmp[:-3] + suffix + handler_intermediate_tmp[-3:]
    )

    final_output_fp = handler_intermediate_tmp[:-3] + suffix + ".zip"

    _create_intermediate_handler_file(
        original_file_location, needed_lines, handler_intermediate_final
    )

    handler_final_info = (handler_intermediate_final, relative_handler_path)
    additional_files_final_info = concatenate(
        [
            _make_additional_file_information(x, base_packaging_path, excludes)
            for x in additional_files
        ]
    )

    handler_hash = writer.create_handler_archive(
        handler_final_info,
        additional_files=additional_files_final_info,
        output_fp=final_output_fp,
    )

    return final_output_fp, handler_hash


def _create_intermediate_handler_file(
    original_path: FilePath, needed_lines: List[int], output_fp: FilePath
) -> None:
    """
    Make the actual file that will be deployed onto a serverless platform by parsing out the needed lines from the original file
    and writing them to provide FilePath

    Args:
        original_path (FilePath): The original file location that this function is from
        needed_lines (List[int]): The list of line numbers needed from the original function
        output_fp (str): The final location of the parsed file
    """
    if not os.path.isfile(original_path):
        raise Exception

    actual_lines = _get_lines_from_file_list(
        _get_file_as_list(original_path), needed_lines
    )

    cleaned_actual_lines = _clean_lines(actual_lines)

    if os.path.isfile(output_fp):
        os.remove(output_fp)
    else:
        Path(os.path.dirname(output_fp)).mkdir(parents=True, exist_ok=True)

    _write_intermediate_function(output_fp, cleaned_actual_lines)


def _make_additional_file_information(
    module: Union[FilePath, DirectoryPath],
    base_directory: DirectoryPath,
    exclude_directories: Set[str] = set(),
) -> List[Tuple[FilePath, FilePath]]:
    """Given a FilePath or Directory Path representing a Relative Module, create all tuples
    of the path to zip location. The returned relative path is based on the provided base_directory.

    Args:
        module (FilePath)
        base_directory (DirectoryPath):
        exclude_directories (Set[str], optional): any sub directory to exclude. Defaults to set().

    Raises:
        Exception: module is not either a file or directory

    Returns:
        List[Tuple[FilePath, FilePath]]: All information to package the module.
    """
    if os.path.isfile(module):
        relative_fp = _get_relative_path(module, base_directory)
        return [(module, relative_fp)]

    elif os.path.isdir(module):
        rv = []

        for dirname, subdirs, files in os.walk(module):
            if dirname.split("/")[-1] in exclude_directories:
                continue

            for filename in files:
                original_path = os.path.join(dirname, filename)
                relative_fp = _get_relative_path(original_path, base_directory)
                rv.append((original_path, relative_fp))

        return rv

    else:
        raise Exception(f"{module} is not either a file or directory")


def _get_file_as_list(path: FilePath) -> List[str]:
    """Return a file as a list of strings

    Args:
        path (FilePath)

    Raises:
        Exception: path is not a file

    Returns:
        List[str]: lines from the file
    """
    if not os.path.isfile:
        raise Exception(f"{path} is not a file")

    with open(path) as fh:
        rv = fh.read().splitlines()

    return rv


def _clean_lines(lines: List[str]) -> List[str]:
    """
    Parsed functions can have empty lines or comments as the last lines of the file, so we are going to start from the end of the file
    and remove those lines. This helps keep the hashes of the handler consistent even if there was changes below the handler that
    are picked up because they are comments.


    Args:
        lines (List[str]): original lines to be added for the handler

    Returns:
        clean_lines (List[str]): Lines with endings trimmed of whitespace and comments
    """

    # final line should be an offset from the end of the list the represents the final real line of python code
    final_line_no = 0

    # Loop through the list from back to start to find the last line of valid python
    for i in range(len(lines) - 1, 0, -1):
        tmp_line = lines[i]

        # if the line is blank it is not a valid line
        if not tmp_line:
            continue

        # if the line is not a comment (starts with '#') or is just whitespace
        if not (tmp_line[0] == "#" or tmp_line.isspace()):
            final_line_no = i
            break

    if final_line_no == 0:
        rv = lines
    else:
        rv = lines[: final_line_no + 1]

    return rv


def _get_lines_from_file_list(file_list: List[str], line_nos: List[int]) -> List[str]:
    """Given a list of string and a list on indexes, return a new list with all indexes from str_list

    Args:
        file_list (List[str]): List of str
        line_nos (List[int]): List of indices

    Returns:
        List[str]
    """
    actual_lines = []

    for i in line_nos:
        if i == -1:
            actual_lines.append(os.linesep)
        elif i <= len(file_list):
            actual_lines.append(file_list[i - 1])

    return actual_lines


def _write_intermediate_function(path: FilePath, lines: List[str]) -> None:
    """
    Write a set of lines for the intermediate handler into the actual file on the system

    Args:
        path (FilePath): Intermediate file path
        lines (List[str]): List of the lines to write
    """

    with open(path, "w") as fh:
        for line in lines:
            fh.write(line)
            fh.write("\n")


def _get_relative_path(original_path: FilePath, base_path: DirectoryPath) -> FilePath:
    """Get the relative path of a file from a given base directory

    Args:
        original_path (FilePath): absolute file path
        base_path (DirectoryPath): base directory

    Returns:
        FilePath: relative file path
    """
    if Path(base_path) not in Path(original_path).parents:
        raise Exception(
            f"""Can not make relative path for {original_path} from {base_path} because it is not a child path"""
        )

    return os.path.relpath(original_path, base_path)
