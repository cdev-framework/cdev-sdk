from typing import List, Optional, Dict
from ast import parse
import os

from pydantic.types import FilePath

from . import utils as fs_utils
from zipfile import ZipFile
from cdev.settings import SETTINGS as cdev_settings
from cdev.utils import paths as cdev_paths, hasher as cdev_hasher
import shutil

INTERMEDIATE_FOLDER = cdev_settings.get("CDEV_INTERMEDIATE_FOLDER_LOCATION")
EXCLUDE_SUBDIRS = {"__pycache__"}

def create_full_deployment_package(original_path : FilePath, needed_lines: List[int], parsed_path: str, pkgs:List[dict]=None ):
    """
    Create all the needed deployment resources needed for a given serverless function. This includes parsing out the needed lines from
    the original function, packaging local dependencies, and packaging external dependencies (pip packages).

    Args:
        original_path (FilePath): The original file location that this function is from
        needed_lines (List[int]): The list of line numbers needed from the original function
        parsed_path (str): The final location of the parsed file
        pkgs (List[Dict]): The list of package info for the function

    Returns:
        src_code_hash (str): The hash of the source code archive 
        handler_archive_location (FilePath): The location of the created archive for the handler
        base_handler_path (str): The path to the file as a python package path
        dependencies_archive_locations (List[FilePath]): Locations of any external dependency archive 
        dependencies_hash (Dict[str,str]): The hash for each of the created dependency archives (layer_name -> hash)
    """
    _make_intermediate_handler_file(original_path, needed_lines, parsed_path)

    # Start from the base intermediate folder location then replace '/' with '.' and final remove the '.py' from the end
    base_handler_path = cdev_paths.get_relative_to_intermediate_path(parsed_path).replace("/", ".")[:-3]


    handler_files = [parsed_path]

    filename = os.path.split(parsed_path)[1]
    zip_archive_location = os.path.join(os.path.dirname(parsed_path), filename[:-3] + ".zip")

    if pkgs:
        pkg_info = _create_package_dependencies_info(pkgs)

    if pkg_info.get("handler_dependencies"):
        # Copy the local dependencies files into the intermediate folder to make packaging easier
        # All the local copied files are added to the set of files needed to be include in the .zip file uploaded as the handler
        local_dependencies_intermediate_locations = _copy_local_dependencies(pkg_info.get("handler_dependencies"))
        handler_files.extend(local_dependencies_intermediate_locations)

    if pkg_info.get("layer_dependencies"):
        dir = os.path.join(INTERMEDIATE_FOLDER, os.path.dirname(parsed_path))
        
        dependencies_info, dependencies_hash  = _make_layers_zips(dir, filename[:-3], pkg_info.get("layer_dependencies") )
        

        
    else:
        dependencies_info = None
        dependencies_hash= None

    src_code_hash = _make_intermediate_handler_zip(zip_archive_location, handler_files)

    return (src_code_hash, zip_archive_location, base_handler_path, dependencies_info, dependencies_hash)


def _create_package_dependencies_info(pkgs) -> Dict:

    layer_dependencies = []
    handler_dependencies = []


    for pkg_name in pkgs:
        pkg = pkgs.get(pkg_name)

        if pkg.get("type") == 'pip':
            layer_dependencies.append({
                "base_folder": pkg.get("fp"),
                "pkg_name": pkg.get("pkg_name")
            })

        elif pkg.get("type") == 'localpackage':
            if cdev_paths.is_in_project(pkg.get("fp")):
                if os.path.isdir(pkg.get("fp")):

                    #Get external dependencies in the folder

                    for dir, _, files in os.walk(pkg.get("fp")):
                        if dir.split("/")[-1] in EXCLUDE_SUBDIRS:
                            continue

                        handler_dependencies.extend([os.path.join( pkg.get("fp"), dir, x) for x in files])
                else:
                    handler_dependencies.append(pkg.get("fp"))
            
    rv = {
        "layer_dependencies": layer_dependencies,
        "handler_dependencies": handler_dependencies
    }


    return rv


def _make_intermediate_handler_file(original_path, needed_lines, parsed_path) -> str:
    """
    Make the actual file that will be deployed onto a serverless platform by parsing out the needed lines from the original file

    Args:
        original_path (FilePath): The original file location that this function is from
        needed_lines (List[int]): The list of line numbers needed from the original function
        parsed_path (str): The final location of the parsed file
    """
    if not os.path.isfile(original_path):
        print(f"nah {original_path}")
        return False


    file_list =  fs_utils.get_file_as_list(original_path)

    actual_lines = fs_utils.get_lines_from_file_list(file_list, needed_lines)

    cleaned_actual_lines = _clean_lines(actual_lines)
    
    _write_intermediate_function(parsed_path, cleaned_actual_lines)


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


def _copy_local_dependencies(files: List[FilePath]) -> List[FilePath]:
    rv = []
    for file in files:
        intermediate_location = cdev_paths.get_full_path_from_intermediate_folder( cdev_paths.get_relative_to_project_path(file))
        rv.append(intermediate_location)

        relative_to_intermediate = cdev_paths.get_relative_to_intermediate_path(intermediate_location).split("/")[:-1]

        cdev_paths.create_path(INTERMEDIATE_FOLDER, relative_to_intermediate)
        shutil.copyfile(file, intermediate_location)


    return rv


def _write_intermediate_function(path, lines):
    # Function takes a filepath (fp), filename, and lines then writes the lines to the file
    # This function is used to create the intermediate file
    # It creates the file on the file system and also returns metadata about the file


    with open(path, "w") as fh:
        for line in lines:
            fh.write(line)
            fh.write("\n")

    return True

def _make_intermediate_handler_zip(zip_archive_location: str, paths: List[str]) -> str:
    hashes = []
    with ZipFile(zip_archive_location, 'w') as zipfile:
        for path in paths:
            filename = os.path.relpath(path,INTERMEDIATE_FOLDER)
            zipfile.write(path, filename)
            hashes.append(cdev_hasher.hash_file(path))

    return cdev_hasher.hash_list(hashes)


def _make_layers_zips(zip_archive_location_directory, basename, needed_info) -> List[FilePath]:
    archives_made = set()
    archive_to_hashlist = {}
    layer_name = "layer1"
    for info in needed_info:
        zip_archive_full_path = os.path.join(zip_archive_location_directory,  basename +"_" + layer_name  + ".zip" )

        if not zip_archive_full_path in archives_made:
            archives_made.add(zip_archive_full_path)
            archive_to_hashlist[layer_name] = {
                "artifact_path": zip_archive_full_path,
                "hash": []
            }

        with ZipFile(zip_archive_full_path, 'w') as zipfile:
            for dirname, subdirs, files in os.walk(info.get("base_folder")):
                if dirname.split("/")[-1] in EXCLUDE_SUBDIRS:
                    continue

                zip_dir_name = os.path.normpath( os.path.join('python', info.get("pkg_name") , os.path.relpath(dirname , info.get("base_folder") ) ) )

                for filename in files:
                    original_path = os.path.join(dirname, filename)
                    zipfile.write(original_path, os.path.join(zip_dir_name, filename))
                    archive_to_hashlist[layer_name]['hash'].append(cdev_hasher.hash_file(original_path))

    archive_to_hash = []
    dependency_info = []
    for layer_name in archive_to_hashlist:
        package_hash = cdev_hasher.hash_list(archive_to_hashlist.get(layer_name).get('hash'))
        archive_to_hash.append(package_hash)
    
        dependency_info.append({
            'name': layer_name,
            'artifact_path': cdev_paths.get_relative_to_project_path( archive_to_hashlist.get(layer_name).get("artifact_path")),
            'hash': package_hash
        })

    return dependency_info, cdev_hasher.hash_list(archive_to_hash)
        

