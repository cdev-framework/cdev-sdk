import os
from pydantic import FilePath
from typing import List, Tuple, Set, Any
from zipfile import ZipFile
from pathlib import Path

from core.utils.hasher import hash_file, hash_list


def create_archive_and_hash(
    file_information: List[Tuple[FilePath, FilePath]], output_fp: FilePath
) -> str:
    """Given a set of file and destinations, write the files to a zip at the destination
    within the zip.

    Args:
        file_information (List[Tuple[FilePath, FilePath]]): List of Filepath and Destinations in the archive
        output_fp (FilePath): destination of the archive

    Returns:
        str: hash of the archive
    """
    hash_val = _create_hash([x[0] for x in file_information])

    _create_archive(file_information, output_fp)

    return hash_val


def _create_hash(files: List[FilePath]) -> str:
    """Given a list of files, create a hash of representing the state of all the files.

    Args:
        files (List[FilePath]): file locations

    Returns:
        str: hash
    """
    tmp_file_hashes = [hash_file(x) for x in files]
    tmp_file_hashes.sort()

    return hash_list(tmp_file_hashes)


def _create_archive(
    file_information: List[Tuple[FilePath, FilePath]],
    output_fp: FilePath,
) -> None:
    """Create a zip archive at the given file path. The list of file inputs should be a tuple of the current file location
    and the final location within the zip file.

    Args:
        file_information (List[Tuple(FilePath, FilePath)]): Original Path to File and Path within Zip archive
        output_fp (FilePath): destination of the archive
    """
    _added_files = set()

    if os.path.isfile(output_fp):
        os.remove(output_fp)

    if not os.path.isdir(os.path.dirname(output_fp)):
        Path(os.path.dirname(output_fp)).mkdir(parents=True, exist_ok=True)

    with ZipFile(output_fp, "a") as zipfile:
        for original_path, zip_path in file_information:
            if original_path not in _added_files:
                zipfile.write(original_path, zip_path)
                _added_files.add(original_path)
