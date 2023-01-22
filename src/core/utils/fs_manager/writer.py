import os
from pydantic import FilePath
from typing import List, Tuple, Set, Any
from zipfile import ZipFile
import itertools
from pathlib import Path

from core.utils.hasher import hash_file, hash_list
from core.utils.cache import Cache
from core.utils import hasher
from .module_types import PackagedModuleInfo, RelativeModuleInfo

deliminator = "-"


def create_handler_archive(
    handler_file: Tuple[FilePath, FilePath],
    output_fp: FilePath,
    additional_files: List[Tuple[FilePath, FilePath]] = [],
):
    """Given a handler and optional additional files, write them to an archive using their relative path to base dir. Base dir
    must be a parent directory to all files provided.

    Args:
        handler_file (Tuple[FilePath, FilePath]): _description_
        output_fp (FilePath): _description_
        additional_files (List[Tuple[FilePath, FilePath]]): _description_. Defaults to [].
    """

    return _create_archive_and_hash([handler_file, *additional_files], output_fp)


def create_layer_archive(
    modules: List[PackagedModuleInfo],
    output_fp: FilePath,
    exclude_subdirectories: Set[set] = {},
    cache: Cache = None,
) -> str:
    """Given a list of packaged module info objects, create an archive that includes all needed files for those modules. If a cache is provide,
    use it to avoid duplicating work.

    Args:
        modules (List[PackagedModuleInfo]): modules.
        output_fp (FilePath): archive output location.
        exclude_subdirectories (Set[set], optional): directories to ignore. Defaults to {}.
        cache (Cache, optional): _description_. Defaults to None.

    Returns:
        str: hash of the created archive
    """
    if cache:
        cache_key = _create_cache_key(modules)
        if cache.in_cache(cache_key) and output_fp == cache.in_cache(cache_key):
            return cache.get_from_cache(cache_key)[1]

        artifact_hash = _create_archive_and_hash(
            file_information=concatenate(
                [
                    _make_file_archive_information(x, exclude_subdirectories)
                    for x in modules
                ]
            ),
            output_fp=output_fp,
        )

        cache.update_cache(cache_key, (output_fp, artifact_hash))

        return artifact_hash

    else:
        return _create_archive_and_hash(
            file_information=concatenate(
                [
                    _make_file_archive_information(x, exclude_subdirectories)
                    for x in modules
                ]
            ),
            output_fp=output_fp,
        )


def _create_cache_key(modules: List[PackagedModuleInfo]) -> str:
    """Create cache key for a given list of package module info objects

    Args:
        modules (List[PackagedModuleInfo])

    Returns:
        str: cache key
    """

    _ids = [f"{x.module_name}{deliminator}{x.tag}" for x in modules]
    _ids.sort()

    return hasher.hash_list(_ids)


def _make_file_archive_information(
    module: PackagedModuleInfo, exclude_subdirectories: Set[set]
) -> List[Tuple[FilePath, FilePath]]:
    """Given a PackagedModuleInfo, create a list of all the files and their location in an archive. If the archive is a
    directory, then create information for all nested files.

    Args:
        module (PackagedModuleInfo)

    Returns:
        List[Tuple[FilePath, FilePath]]: Original Path to File and Path within Zip archive
    """
    base_packages_dir = os.path.split(module.absolute_fs_position)[0]
    # Sometimes the RECORD file (jmespath) will point to parent directories, but we do not want to allow that
    needed_top_artifacts = set(
        filter(
            lambda x: not x.startswith(".."),
            _get_all_top_directories_from_record(module.record_location),
        )
    )

    rv = []
    for top_artifact in needed_top_artifacts:
        absolute_location = os.path.join(base_packages_dir, top_artifact)

        if os.path.isfile(absolute_location):
            # this is a single python file not a folder (ex: six.py)
            # since this is a module that is just a single file plop in /python/<filename> and it will be on the pythonpath
            rv.append((absolute_location, os.path.join("python", top_artifact)))

        else:
            rv.extend(
                _generate_file_archive_file_for_directory(
                    absolute_location, exclude_subdirectories
                )
            )

    return rv


def _generate_file_archive_file_for_directory(
    directory: str, exclude_subdirectories: Set[str] = set()
) -> List[Tuple[str, str]]:
    """Given a directory that contains a packaged python module, return the list of tuples for all artifacts in that directory.
    The first element of the tuple should the original path of the artifact and the second element should be the location the
    file needs to be placed in for the final generated archive.

    Args:
        directory (str): Directory to generate for
        exclude_subdirectories (Set[str]): optional parameter if there are sub directories that should be ignore (__pycache__)

    Returns:
        List[Tuple[str,str]]
    """
    rv = []
    top_directory_name = os.path.split(directory)[1]
    for dirname, subdirs, files in os.walk(directory):
        if dirname.split("/")[-1] in exclude_subdirectories:
            continue

        zip_dir_name = os.path.normpath(
            os.path.join(
                "python",
                top_directory_name,
                os.path.relpath(dirname, directory),
            )
        )

        for filename in files:
            original_path = os.path.join(dirname, filename)
            rv.append((original_path, os.path.join(zip_dir_name, filename)))

    return rv


def _get_all_top_directories_from_record(record_location: str) -> Set[str]:
    """Given the location of a RECORD file, return all the top level directories that are needed.

    Args:
        record_location (str)

    Returns:
        Set[str]
    """
    with open(record_location, "r") as fh:
        _all_files = fh.readlines()

    return set([x.split(",")[0].split("/")[0] for x in _all_files])


def _create_archive_and_hash(
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


def concatenate(lists: List[List[Any]]) -> List[Any]:
    """Helper function to combine a List of List into a single List

    Args:
        lists List[List[Any]]

    Returns:
        List[Any]
    """
    return list(itertools.chain.from_iterable(lists))
