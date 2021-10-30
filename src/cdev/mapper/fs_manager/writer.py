from typing import List, Optional, Dict
from ast import parse
import os

from pydantic.types import FilePath

from . import utils as fs_utils
from zipfile import ZipFile
from cdev.settings import SETTINGS as cdev_settings
from cdev.utils import paths as cdev_paths
import shutil

INTERMEDIATE_FOLDER = cdev_settings.get("CDEV_INTERMEDIATE_FOLDER_LOCATION")

def create_full_deployment_package(original_path : FilePath, needed_lines: List[int], parsed_path: str, pkgs:List[dict]=None ):
    _make_intermediate_handler_file(original_path, needed_lines, parsed_path)
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
        
        _make_layers_zips(dir, filename[:-3], pkg_info.get("layer_dependencies") )

    _make_intermediate_handler_zip(zip_archive_location, handler_files)

    return (123, "helloworld23", zip_archive_location)


EXCLUDE_SUBDIRS = {"__pycache__"}

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


def _make_intermediate_handler_file(original_path, needed_lines, parsed_path):
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

def _make_intermediate_handler_zip(zip_archive_location: str, paths: List[str]):
    with ZipFile(zip_archive_location, 'w') as zipfile:
        for path in paths:
            filename = os.path.relpath(path,INTERMEDIATE_FOLDER)
            zipfile.write(path, filename)
            


def _make_layers_zips(zip_archive_location_directory, basename, needed_info):

    for info in needed_info:
        zip_archive_full_path = os.path.join(zip_archive_location_directory,  basename + "_layer1" + ".zip" )
        with ZipFile(zip_archive_full_path, 'w') as zipfile:
            for dirname, subdirs, files in os.walk(info.get("base_folder")):
                if dirname.split("/")[-1] in EXCLUDE_SUBDIRS:
                    continue

                zip_dir_name = os.path.normpath( os.path.join('python', info.get("pkg_name") , os.path.relpath(dirname , info.get("base_folder") ) ) )

                for filename in files:
                    zipfile.write(os.path.join(dirname, filename), os.path.join(zip_dir_name, filename))
    
       
        

