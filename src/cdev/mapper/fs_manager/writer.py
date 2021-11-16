from typing import List, Optional, Dict, Tuple
from ast import parse
import os
from pydantic.main import BaseModel

from pydantic.types import DirectoryPath, FilePath
from sortedcontainers.sorteddict import SortedDict

from . import utils as fs_utils
from .utils import PackageTypes, ModulePackagingInfo, LocalDependencyArchiveInfo, ExternalDependencyWriteInfo

from zipfile import ZipFile
from cdev.settings import SETTINGS as cdev_settings
from cdev.utils import paths as cdev_paths, hasher as cdev_hasher
import json
import shutil

INTERMEDIATE_FOLDER = cdev_settings.get("CDEV_INTERMEDIATE_FOLDER_LOCATION")
EXCLUDE_SUBDIRS = {"__pycache__"}

CACHE_LOCATION = os.path.join(cdev_settings.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "writercache.json")


class LayerWriterCache:
    """
    Naive cache implentation for writing zip files for the lambda layers.  
    """

    def __init__(self) -> None:

        if not os.path.isfile(CACHE_LOCATION):
            self._cache = {}

        else:

            with open(CACHE_LOCATION) as fh:
                self._cache = json.load(fh)


    def find_item(self, id: str):
        return self._cache.get(id)


    def add_item(self, id: str, item: json):
        self._cache[id] = item

        with open(CACHE_LOCATION, "w") as fh:
            json.dump(self._cache, fh, indent=4)

LAYER_CACHE = LayerWriterCache()


def create_full_deployment_package(original_path : FilePath, needed_lines: List[int], parsed_path: str, pkgs: Dict[str, ModulePackagingInfo]=None ):
    """
    Create all the needed deployment resources needed for a given serverless function. This includes parsing out the needed lines from
    the original function, packaging local dependencies, and packaging external dependencies (pip packages).

    Args:
        original_path (FilePath): The original file location that this function is from
        needed_lines (List[int]): The list of line numbers needed from the original function
        parsed_path (str): The final location of the parsed file
        pkgs (Dict[str, ModulePackagingInfo]): The list of package info for the function

    Returns:
        src_code_hash (str): The hash of the source code archive 
        handler_archive_location (FilePath): The location of the created archive for the handler
        base_handler_path (str): The path to the file as a python package path
        external_dependency_information (LocalDependencyArchiveInfo): Information about the external dependencies
    """

    dependencies_info = None

    # Write the actual parsed function into an intermediate folder
    _make_intermediate_handler_file(original_path, needed_lines, parsed_path)
    handler_files = [parsed_path]

    # The handler can be in a subdirectory and since we preserve the relative project structure, we need to bring any __init__.py files
    # to make sure the handler is in a valid path
    extra_handler_path_files = _find_packaging_files_handler(original_path)
    

    handler_files.extend(extra_handler_path_files)

    # Start from the base intermediate folder location then replace '/' with '.' and final remove the '.py' from the end
    base_handler_path = cdev_paths.get_relative_to_intermediate_path(parsed_path).replace("/", ".")[:-3]

    filename = os.path.split(parsed_path)[1]
    zip_archive_location = os.path.join(os.path.dirname(parsed_path), filename[:-3] + ".zip")

    if pkgs:
        
        

        layer_dependencies, handler_dependencies = _create_package_dependencies_info(pkgs)

        if layer_dependencies:
            # Make the layer archive in the same folder as the handler 
            archive_dir = os.path.join(INTERMEDIATE_FOLDER, os.path.dirname(parsed_path))
            dependencies_info = _make_layers_zips(archive_dir, filename[:-3], layer_dependencies )
    
        if handler_dependencies:
            # Copy the local dependencies files into the intermediate folder to make packaging easier
            # All the local copied files are added to the set of files needed to be include in the .zip file uploaded as the handler
            # Add their copied locations into the handler_files var so that they are written to the final handler archive
            local_dependencies_intermediate_locations = _copy_local_dependencies(handler_dependencies)
            handler_files.extend(local_dependencies_intermediate_locations)



    # Create the actual handler archive by zipping the needed files
    src_code_hash = _make_intermediate_handler_zip(zip_archive_location, handler_files)

    return (src_code_hash, zip_archive_location, base_handler_path, dependencies_info)



def _create_package_dependencies_info(pkgs: Dict[str, ModulePackagingInfo]) -> Tuple[List[ExternalDependencyWriteInfo], List[str]]:
    """
    Take a dictionary of the top level packages (str [pkg_name] -> ModulePackagingInfo) that are used by a handler and return the 
    necessary information for creating the deployment packages. Packages can be broken down into two categories: handler and layer.

    Args:
        pkgs (Dict[str, ModulePackagingInfo]): Top level packages used by the handler


    Returns:
        layer_dependencies (List[ExternalDependencyWriteInfo]): The packages to be added to the layers
        handler_dependencies (List[str]): List of files to include with the handler
    
    Handler packages are located within the 'cdev project', and therefore, should be packaged into the handler archive so that they 
    remain in the correct relative location to the handler function.
        src:\n
        |_ views\n
        |___ handlers.py\n
        |_ models\n
        |___ model.py\n

    If a function in the handlers.py file references models.py as a relative package (from .. import models or from src import models) 
    it is important to keep the relative file structure the same

    Layer packages are packages that are found on the PYTHONPATH and most likely installed with a package manager like PIP. These 
    should be packages as layers to keep the handler archive size small.

    Note that the input are the top level packages used by the handler, so we must look at the 'flat' attribute to find all the 
    needed dependencies.
    """

    layer_dependencies = []
    handler_dependencies = set()


    for pkg_name in pkgs:
        pkg = pkgs.get(pkg_name)

        if pkg.type == PackageTypes.PIP:
            layer_dependencies.append(ExternalDependencyWriteInfo(**{
                "location": pkg.fp,
                "id": pkg.get_id_str()
            }))

            

        elif pkg.type == PackageTypes.LOCALPACKAGE:
            if cdev_paths.is_in_project(pkg.fp):
                if os.path.isdir(pkg.fp):

                    # If the fp is a dir that means we need to include the entire directory

                    for dir, _, files in os.walk(pkg.fp):
                        if dir.split("/")[-1] in EXCLUDE_SUBDIRS:
                            continue

                        handler_dependencies = handler_dependencies.union(set([os.path.join( pkg.fp, dir, x) for x in files]))
                else:

                    handler_dependencies.add(pkg.fp)
            
       
        if pkg.flat:
            for dependency in pkg.flat:
                if dependency.type == PackageTypes.PIP:
                    layer_dependencies.append(ExternalDependencyWriteInfo(**{
                        "location": dependency.fp,
                        "id": dependency.get_id_str()
                    }))


                elif dependency.type == PackageTypes.LOCALPACKAGE:
                    handler_dependencies.add( dependency.fp )

            
    return (layer_dependencies, list(handler_dependencies))


def _make_intermediate_handler_file(original_path: FilePath, needed_lines: List[int], parsed_path: str):
    """
    Make the actual file that will be deployed onto a serverless platform by parsing out the needed lines from the original file
    and writing them to an intermediate file

    Args:
        original_path (FilePath): The original file location that this function is from
        needed_lines (List[int]): The list of line numbers needed from the original function
        parsed_path (str): The final location of the parsed file
    """
    if not os.path.isfile(original_path):
        raise Exception


    file_list =  fs_utils.get_file_as_list(original_path)

    actual_lines = fs_utils.get_lines_from_file_list(file_list, needed_lines)

    cleaned_actual_lines = _clean_lines(actual_lines)
    
    _write_intermediate_function(parsed_path, cleaned_actual_lines)

    

def _find_packaging_files_handler(original_path: FilePath) -> List[FilePath]:
    """
    This adds additional files like __init__.py need to make the file work. Since the handler can be in submodules, it is important 
    to find all the nested __init__.py files for making sure the handler is accessible. 

    Args:
        original_path (FilePath): The original path of the file 

    Returns:
        needed_files (List[Filepath]): The list of files that need to be included with the handler
    """
    path_from_project_dir = os.path.dirname(cdev_paths.get_relative_to_project_path(original_path)).split('/')
    intermediate_location = cdev_paths.get_project_path()
    rv = []
    
    while path_from_project_dir:
        
        intermediate_location = os.path.join(intermediate_location, path_from_project_dir.pop(0))
        
        file_loc = os.path.join(intermediate_location, "__init__.py")
        intermediate_file_location = cdev_paths.get_full_path_from_intermediate_folder(cdev_paths.get_relative_to_project_path(file_loc))
       
        if os.path.isfile(file_loc):
            shutil.copyfile(file_loc, intermediate_file_location)   
        else:
            with open(intermediate_file_location, 'a'):
                os.utime(intermediate_file_location)


        rv.append(intermediate_file_location)

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


def _copy_local_dependencies(dependencies: List[FilePath]) -> List[FilePath]:
    """
    Copy the local dependency files from their original location into the intermediate folder with the actual handler.
    This step makes the archiving step simplier since all the need files are in the intermediate folder.

    Args:
        file_locations (List[str]): list of file locations that need to be copied

    Returns:
        copied_file_locations (List[str]): list of locations of the copied files
    """
    rv = []
    for dependency in dependencies:
        intermediate_location = cdev_paths.get_full_path_from_intermediate_folder( cdev_paths.get_relative_to_project_path(dependency))
        

        
        relative_to_intermediate = cdev_paths.get_relative_to_intermediate_path(intermediate_location).split("/")[:-1]
        
        cdev_paths.create_path(INTERMEDIATE_FOLDER, relative_to_intermediate)
        

        if os.path.isdir(dependency):
            if os.path.isdir(intermediate_location):
                shutil.rmtree(intermediate_location)

            shutil.copytree(dependency, intermediate_location, ignore=shutil.ignore_patterns('*.pyc'))

            for dir_name,_,files in os.walk(intermediate_location):
                for file in files:
                    rv.append(os.path.join(dir_name,file))

        elif os.path.isfile(dependency):
            shutil.copyfile(dependency, intermediate_location)
            rv.append(intermediate_location)
        else:
            raise Exception


    return rv


def _write_intermediate_function(path: FilePath, lines: List[str]):
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
    



def _make_intermediate_handler_zip(zip_archive_location: str, paths: List[FilePath]) -> str:
    """
    Make the archive for the handler deployment. 

    Args:
        zip_archive_location (str): The file path for the archive. Might not be created yet
        paths (List[FilePath]): The list of files that should be written to the archive

    Returns:
        archive_hash (str): An identifying hash for the zip
    """
    hashes = []
    with ZipFile(zip_archive_location, 'w') as zipfile:
        for path in paths:
            filename = os.path.relpath(path, INTERMEDIATE_FOLDER)
            zipfile.write(path, filename)
            hashes.append(cdev_hasher.hash_file(path))

    return cdev_hasher.hash_list(hashes)



def _make_layers_zips(zip_archive_location_directory: DirectoryPath, basename: str, needed_info: List[ExternalDependencyWriteInfo]) -> LocalDependencyArchiveInfo:
    """
    Create the zip archive that will be deployed with the handler function. This function uses a cache to determine if there is already an archive available to 
    use. All modules provide are written to a single archive such that the module is in '/python/<module_name>'.

    Args:
        zip_archive_location_directory (DirectoryPath): The directory that the archive will be created in.
        basename (str): base name for the archive
        needed_info (List[ExternalDependencyWriteInfo]): The information about what modules to add to the archive

    Returns:
        info (LocalDependencyArchiveInfo): information about the artifact that was created
    """

    # Create a hash of the ids of the packages to see if there is an already available archive to use
    ids = [x.id for x in needed_info]
    ids.sort()

    _id_hashes = cdev_hasher.hash_list(ids)
    cache_item = LAYER_CACHE.find_item(_id_hashes)
    if cache_item:
        return LocalDependencyArchiveInfo(**cache_item)

    layer_name = basename + "_layer"
    _file_hashes = []    
    zip_archive_full_path = os.path.join(zip_archive_location_directory,  layer_name + ".zip" )
    seen_pkgs = set()

    if os.path.isfile(zip_archive_full_path):
        os.remove(zip_archive_full_path)

    for info in needed_info:
        if info.id in seen_pkgs:
            continue

        seen_pkgs.add(info.id)
        

        with ZipFile(zip_archive_full_path, 'a') as zipfile:
            if os.path.isfile(info.location):
                # this is a single python file not a folder (ex: six.py)
                file_name = os.path.split(info.location)[1]
                # since this is a module that is just a single file plop in /python/<filename> and it will be on the pythonpath

                zipfile.write(info.location, os.path.join('python', file_name))
                _file_hashes.append(cdev_hasher.hash_file(info.location))


            else:
                pkg_name = os.path.split(info.location)[1]

                for dirname, subdirs, files in os.walk(info.location):
                    if dirname.split("/")[-1] in EXCLUDE_SUBDIRS:
                        continue
                    
                    zip_dir_name = os.path.normpath( os.path.join('python', pkg_name , os.path.relpath(dirname , info.location ) ) )
    
                    for filename in files:
                        original_path = os.path.join(dirname, filename)
                        zipfile.write(original_path, os.path.join(zip_dir_name, filename))
                        _file_hashes.append(cdev_hasher.hash_file(original_path))

                pkg_dir = os.path.dirname(info.location)
                for obj in os.listdir(pkg_dir):
                    # Search in the general packaging directory for any other directory with the package name
                    # for example look for numpy.lib when including numpy
                    if os.path.join(pkg_dir, obj) == info.location:
                        continue

                    
                    if os.path.isdir(os.path.join(pkg_dir, obj)) and obj.split(".")[0] == os.path.split(info.location)[1]:
                        for dirname, subdirs, files in os.walk( os.path.join(pkg_dir, obj) ):
                            if dirname.split("/")[-1] in EXCLUDE_SUBDIRS:
                                continue
                            
                            zip_dir_name = os.path.normpath( os.path.join('python', obj , os.path.relpath(dirname , os.path.join(pkg_dir, obj) ) ) )

                            for filename in files:
                                original_path = os.path.join(dirname, filename)
                                zipfile.write(original_path, os.path.join(zip_dir_name, filename))
                                _file_hashes.append(cdev_hasher.hash_file(original_path))
                        

    full_archive_hash = cdev_hasher.hash_list(_file_hashes)
    
    dependency_info = LocalDependencyArchiveInfo(**{
        'name': layer_name,
        'artifact_path': cdev_paths.get_relative_to_project_path(zip_archive_full_path),
        'hash': full_archive_hash
    })
    

    # convert to json string then back to python object because it has a Filepath type in it and that is always handled weird. 
    LAYER_CACHE.add_item(_id_hashes, json.loads(dependency_info.json()))

    return dependency_info
        

