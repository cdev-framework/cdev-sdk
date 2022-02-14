import heapq
import json
import math
import os
from pydantic.types import DirectoryPath, FilePath
import shutil
from typing import List, Dict, Tuple, Set
from zipfile import ZipFile
from core.constructs.workspace import Workspace


from core.utils import paths as core_paths, hasher as cdev_hasher
from core.utils.logger import log
from core.default.resources.simple.xlambda import  DependencyLayer


from . import utils as fs_utils
from .utils import PackageTypes, ModulePackagingInfo, ExternalDependencyWriteInfo
from .external_dependencies_index import weighted_dependency_graph, compute_index



EXCLUDE_SUBDIRS = {"__pycache__"}



class LayerWriterCache:
    """
    Naive cache implentation for writing zip files for the lambda layers.
    """

    def __init__(self, cache_location: str) -> None:
        self._cache_location = cache_location
        if not os.path.isfile(self._cache_location):
            self._cache = {}

        else:
            with open(self._cache_location) as fh:
                self._cache = json.load(fh)

    def find_item(self, id: str):
        return self._cache.get(id)

    def add_item(self, id: str, item: json):
        self._cache[id] = item

        with open(self._cache_location , "w") as fh:
            json.dump(self._cache, fh, indent=4)


LAYER_CACHE = LayerWriterCache(os.path.join(os.getcwd(),".cache") )


def create_full_deployment_package(
    original_path: FilePath,
    needed_lines: List[int],
    function_name: str,
    base_archive_directory: DirectoryPath,
    pkgs: Dict[str, ModulePackagingInfo] = None,
    available_layers: int = 5,
):
    """
    Create all the needed deployment resources needed for a given serverless function. This includes parsing out the needed lines from
    the original function, packaging local dependencies, and packaging external dependencies (pip packages).

    Args:
        original_path (FilePath): The original file location that this function is from
        needed_lines (List[int]): The list of line numbers needed from the original function
        function_name (str): The name of the function
        base_archive_directory (DirectoryPath): Base path to write final archives
        pkgs (Dict[str, ModulePackagingInfo]): The list of package info for the function
        available_layers (int): The number of layers available to use

    Returns:
        handler_archive_location (FilePath): The location of the created archive for the handler
        handler_archive_hash (str): Identifying hash of the handler archive
        base_handler_path (str): The path to the file as a python package path. This will be the handler entry point when deployed.
        external_dependencies (LambdaLayerArtifact): List of layers that are needed for this function
    """
    global LAYER_CACHE

    LAYER_CACHE = LayerWriterCache(os.path.join(base_archive_directory, "cache"))

    # Clean the name of the function and create the final path of the parsed function
    cleaned_name = function_name.replace(" ", "_")   
    parsed_path = fs_utils.get_parsed_path(original_path, cleaned_name, base_archive_directory)
    log.debug("Parsed Path (%s) for %s/%s", parsed_path, original_path, cleaned_name)

    # Write the actual parsed function into an intermediate folder
    _make_intermediate_handler_file(original_path, needed_lines, parsed_path)

    # Keeps track of all files that need to be include in the handler archive
    handler_files = [parsed_path]

    # The handler can be in a subdirectory and since we preserve the relative project structure, we need to bring any __init__.py files
    # to make sure the handler is in a valid path
    extra_handler_path_files = _find_packaging_files_handler(original_path, base_archive_directory)

    handler_files.extend(extra_handler_path_files)

    # Start from the base archive folder location then replace '/' with '.' and final remove the '.py' from the end
    base_handler_path = os.path.relpath(
        parsed_path,
        start=base_archive_directory
    ).replace("/", ".")[:-3]

    # Zip archive will be at the same directory as the handler and replaced '.py' with '.zip
    parsed_filename = os.path.split(parsed_path)[1]
    zip_archive_location = os.path.join(
        os.path.dirname(parsed_path), parsed_filename[:-3] + ".zip"
    )

    dependencies_info: List[DependencyLayer] = []

    if pkgs:
        # Based on the directly references modules in the handler
        # Figure out the optimal modules to package to need the needs. 
        layer_dependencies, handler_dependencies = _create_package_dependencies_info(
            pkgs
        )

        if layer_dependencies:
            # Make the layer archive in the same folder as the handler

            LAYERS_DIR_NAME = "layers"

            archive_dir = os.path.join(
                base_archive_directory, LAYERS_DIR_NAME
            )

            if not os.path.isdir(archive_dir):
                os.mkdir(archive_dir)

            (
                single_dependency_layers,
                composite_layer,
            ) = _create_layers_from_referenced_modules(
                layer_dependencies, available_layers
            )
                    

            if single_dependency_layers:
                for single_layer in single_dependency_layers:
                    dependencies_info.append(
                        _make_single_dependency_archive(single_layer, archive_dir)
                    )

            if composite_layer:
                dependencies_info.append(
                    _make_composite_dependency_archive(composite_layer, archive_dir)
                )

        if handler_dependencies:
            # Copy the local dependencies files into the intermediate folder to make packaging easier
            # All the local copied files are added to the set of files needed to be include in the .zip file uploaded as the handler
            # Add their copied locations into the handler_files var so that they are written to the final handler archive
            local_dependencies_intermediate_locations = _copy_local_dependencies(
                handler_dependencies,
                base_archive_directory
            )
            handler_files.extend(local_dependencies_intermediate_locations)


    # Create the actual handler archive by zipping the needed files
    archive_hash = _make_intermediate_handler_zip(zip_archive_location, handler_files, base_archive_directory)

    return (zip_archive_location, archive_hash, base_handler_path, dependencies_info)


def _create_package_dependencies_info(
    directly_referenced_pkgs: Dict[str, ModulePackagingInfo]
) -> Tuple[List[ModulePackagingInfo], List[str]]:
    """
    Take a dictionary of the directly referenced packages (str [pkg_name] -> ModulePackagingInfo) that are used by a handler and return the
    necessary information for creating the deployment packages.

    Args:
        pkgs (Dict[str, ModulePackagingInfo]): Directly referenced packages used by the handler

    Returns:
        layer_dependencies (List[ModulePackagingInfo]): The packages to be added to the layers
        handler_dependencies (List[str]): List of files to include with the handler
    
    Packages can be broken down into two categories: handler and layer.

    
    Handler packages are located within the `Workspace`, and therefore, should be packaged into the handler archive so that they
    remain in the correct relative location to the handler function.
        src:\n
        |_ views\n
        |___ handlers.py\n
        |_ models\n
        |___ model.py\n

    If a function in the handlers.py file references models.py as a relative package (from .. import models) it is important to keep 
    the relative file structure the same.

    Layer packages are packages that are found on the PYTHONPATH and installed with a package manager like PIP. These
    should be packages as layers to keep the handler archive size small. Read the Cdev dependency deep dives for an in depth breakdown of
    how the layers are being packaged.

    Note that the input are the directly referenced packages used by the handler, so we must look at the 'flat' attribute to find all the
    needed dependencies.
    """

    handler_dependencies = set()
    directly_referenced_module_write_info: Set[ModulePackagingInfo] = set()

    for _, pkg in directly_referenced_pkgs.items():

        if pkg.type == PackageTypes.PIP:
            directly_referenced_module_write_info.add(pkg)

        elif pkg.type == PackageTypes.LOCALPACKAGE:
            full_path  = core_paths.get_full_path_from_workspace_base(pkg.fp)
            if core_paths.is_in_workspace(full_path):
                if os.path.isdir(pkg.fp):
                    # If the fp is a dir that means we need to include the entire directory
                    for dir, _, files in os.walk(pkg.fp):
                        if dir.split("/")[-1] in EXCLUDE_SUBDIRS:
                            # If the directory is in the excluded subdirs then we can just continue
                            # i.e __pycache__
                            continue

                        handler_dependencies = handler_dependencies.union(
                            set([os.path.join(pkg.fp, dir, x) for x in files])
                        )
                else:
                    handler_dependencies.add(pkg.fp)
            else:
                # Can not link to a locally managed module that is not within the cdev project structure.
                print(f"Linking to local module outside of Workspace {pkg.fp}")
                raise Exception

            if pkg.flat:
                # If the local module has dependencies, we need to recursively search them for import statements
                directly_referenced_module_write_info.update(
                    _recursively_find_directly_referenced_modules_in_local_module(pkg)
                )

                for dependency in pkg.flat:
                    if dependency.type == PackageTypes.LOCALPACKAGE:
                        handler_dependencies.add(dependency.fp)

    return (list(directly_referenced_module_write_info), list(handler_dependencies))


def _create_layers_from_referenced_modules(
    directly_referenced_modules: List[ModulePackagingInfo], available_layers: int = 2
) -> Tuple[List[ModulePackagingInfo], List[ModulePackagingInfo]]:
    """
    Run the optimization calculations for creating single dependencies and composite dependencies for the external modules used. Returns the list of modules that should be
    in single dependencies and in the composite layer.

    Args:
        directly_referenced_modules (List[ModulePackagingInfo]): The modules that are directly reference
        available_layers (int): Amount of layers that are available to be used to package the dependencies

    Returns:
        Single Dependency Layers (List[ModulePackagingInfo]): The list of dependencies that should be individual layers
        Composite Dependency Layers (List[ModulePackagaingInfo]): The list of dependencies that go into the composite layer
    """

    # Now that we have all the directly referenced import statements that are for packaged modules, we compute a weighted DAG to create
    # an optimized deployment platform
    # For a more detailed look at this optimization process read the dependency deep dive on the cdev website.
    graph = weighted_dependency_graph(directly_referenced_modules)


    directly_referenced_modules_removed = set(directly_referenced_modules).difference(
        graph.true_top_level_modules
    )


    # Optimization algorithm:
    # Since there is only one available layer, everything must go into the composite layer
    if available_layers == 1:
        return [], graph.true_top_level_modules

    # if the true top level modules is less than (or equal to) the available layers then use a layer for each top level module
    # so that the top level module layer can be reused within the project
    elif len(graph.true_top_level_modules) <= available_layers:
        return graph.true_top_level_modules, []

    # If there are not enough layers available for all the top level modules, we need to create a composite layer that contains more
    # than one top level module. We will create 1 composite layer and N amount of single layers such that the single layers remove the
    # most amount of code that needs to be uploaded in the composite layer.
    else:
        max_index_level = 2
        # We want the index to be the lower of the two:
        # The user defined max index size (so they can cap computer and memory time of the index)
        # The available layers that can be used for single dependencies
        index_depth = min(max_index_level, available_layers)

        
        index = compute_index(graph, index_depth)
        for pair, value in index.items():
            print(f"{pair} -> {math.floor(value/1024)} KB")

        index_heap = [(-value, key) for key, value in index.items()]
        heapq.heapify(index_heap)

        single_dependency_layer_ids = heapq.heappop(index_heap)[1]

        single_dependency_layers: List[ModulePackagingInfo] = []
        composite_layer: List[ModulePackagingInfo] = []

        for dependency in graph.true_top_level_modules:
            if dependency.get_id_str() in single_dependency_layer_ids:
                single_dependency_layers.append(dependency)
            else:
                composite_layer.append(dependency)

        return single_dependency_layers, composite_layer


def _recursively_find_directly_referenced_modules_in_local_module(
    local_module: ModulePackagingInfo,
) -> Set[ModulePackagingInfo]:
    rv = set()
    if local_module.tree:
        for child in local_module.tree:
            if child.type == PackageTypes.PIP:
                rv.add(child)

            elif child.type == PackageTypes.LOCALPACKAGE:
                rv.update(
                    _recursively_find_directly_referenced_modules_in_local_module(child)
                )

    return rv


def _make_intermediate_handler_file(
    original_path: FilePath, needed_lines: List[int], parsed_path: str
):
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

    file_list = fs_utils.get_file_as_list(original_path)

    actual_lines = fs_utils.get_lines_from_file_list(file_list, needed_lines)

    cleaned_actual_lines = _clean_lines(actual_lines)

    _write_intermediate_function(parsed_path, cleaned_actual_lines)


def _find_packaging_files_handler(original_path: FilePath, base_intermediate_path: DirectoryPath) -> List[FilePath]:
    """
    This adds additional files like __init__.py that are needed to make the file work. Since the handler can be in submodules, 
    it is important to find all the nested __init__.py files for making sure the handler is accessible.

    Args:
        original_path (FilePath): The original path of the file

    Returns:
        needed_files (List[Filepath]): The list of files that need to be included with the handler
    """
    path_from_project_dir = os.path.dirname(
        core_paths.get_relative_to_workspace_path(original_path)
    ).split("/")

    tmp = ""
    actual_base_path = Workspace.instance().settings.BASE_PATH
    rv = []

    # Traverse the directory path looking for __init__.py files. If an __init__.py is found then copy it over
    # else just make an empty one   
    while path_from_project_dir:

        tmp = os.path.join(
            tmp, path_from_project_dir.pop(0)
        )

        file_loc = os.path.join(actual_base_path, tmp, "__init__.py")

        intermediate_file_location = os.path.join(base_intermediate_path, tmp, "__init__.py")

        if os.path.isfile(file_loc):
            shutil.copyfile(file_loc, intermediate_file_location)
        else:
            with open(intermediate_file_location, "a"):
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

    for i in range(len(lines) - 1):
        tmp_line = lines[-(i + 1)]

        # if the line is blank it is not a valid line
        if not tmp_line:
            continue

        # if the line is a comment (starts with '#') or is just whitespace
        if not (tmp_line[0] == "#" or tmp_line.isspace()):
            final_line_no = i
            break

    if final_line_no == -1 or final_line_no == 0:
        rv = lines
    else:
        rv = lines[:-final_line_no]

    return rv


def _copy_local_dependencies(dependencies: List[FilePath], base_final_dir: DirectoryPath) -> List[FilePath]:
    """
    Copy the local dependency files from their original location into the intermediate folder with the actual handler.
    This step makes the archiving step simplier since all the need files are in the intermediate folder.

    Args:
        file_locations (List[str]): list of file locations that need to be copied
        base_final_dir (DirectoryPath): base path for copied files

    Returns:
        copied_file_locations (List[str]): list of locations of the copied files
    """
    rv = []


    for dependency in dependencies:
        intermediate_location = os.path.join(
            base_final_dir,
            core_paths.get_relative_to_workspace_path(dependency)
        )

        relative_to_intermediate = core_paths.get_relative_to_intermediate_path(
            intermediate_location
        ).split("/")[:-1]

        core_paths.create_path(base_final_dir, relative_to_intermediate)

        if os.path.isdir(dependency):
            if os.path.isdir(intermediate_location):
                shutil.rmtree(intermediate_location)

            shutil.copytree(
                dependency,
                intermediate_location,
                ignore=shutil.ignore_patterns("*.pyc"),
            )

            for dir_name, _, files in os.walk(intermediate_location):
                for file in files:
                    rv.append(os.path.join(dir_name, file))

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


def _make_intermediate_handler_zip(
    zip_archive_location: str, paths: List[FilePath], base_path: DirectoryPath
) -> str:
    """
    Make the archive for the handler deployment.

    Args:
        zip_archive_location (str): The file path for the archive. Might not be created yet
        paths (List[FilePath]): The list of files that should be written to the archive

    Returns:
        archive_hash (str): An identifying hash for the zip
    """
    hashes = []
    paths.sort()
    with ZipFile(zip_archive_location, "w") as zipfile:
        for path in paths:
            filename = os.path.relpath(path, base_path)
            zipfile.write(path, filename)
            hashes.append(cdev_hasher.hash_file(path))

    return cdev_hasher.hash_list(hashes)


def _make_single_dependency_archive(
    module_info: ModulePackagingInfo, archive_dir: DirectoryPath
) -> DependencyLayer:
    needed_info: List[ExternalDependencyWriteInfo] = []
    

    needed_info.append(
        ExternalDependencyWriteInfo(
            **{"location": module_info.fp, "id": module_info.get_id_str()}
        )
    )

    for child in module_info.flat:
        if not child.type == PackageTypes.PIP:
            continue

        needed_info.append(
            ExternalDependencyWriteInfo(
                **{"location": child.fp, "id": child.get_id_str()}
            )
        )

    # Create a hash of the ids of the packages to see if there is an already available archive to use
    ids = [x.id for x in needed_info]
    ids.sort()

    _id_hashes = cdev_hasher.hash_list(ids)
    cache_item = LAYER_CACHE.find_item(_id_hashes)

    layer_name = module_info.get_id_str()

    if cache_item:
        return DependencyLayer(
            cdev_name=layer_name, artifact_path=cache_item[0], artifact_hash=cache_item[1]
        )

    archive_path, archive_hash = _make_layers_zips(archive_dir, layer_name, needed_info)

    LAYER_CACHE.add_item(_id_hashes, (archive_path, archive_hash))

    return DependencyLayer(cdev_name=layer_name, artifact_path=archive_path, artifact_hash=archive_hash)


def _make_composite_dependency_archive(
    module_info: List[ModulePackagingInfo], archive_dir: DirectoryPath
) -> DependencyLayer:
    needed_info: Set[ExternalDependencyWriteInfo] = set()

    print(f"Making Composite layer")
    for module in module_info:
        needed_info.add(
            ExternalDependencyWriteInfo(
                **{"location": module.fp, "id": module.get_id_str()}
            )
        )

        for child in module.flat:
            print(f"Adding  {child}")
            if not child.type == PackageTypes.PIP:
                continue

            needed_info.add(
                ExternalDependencyWriteInfo(
                    **{"location": child.fp, "id": child.get_id_str()}
                )
            )

    # Create a hash of the ids of the packages to see if there is an already available archive to use
    ids = [x.id for x in needed_info]
    ids.sort()

    _id_hashes = cdev_hasher.hash_list(ids)
    cache_item = LAYER_CACHE.find_item(_id_hashes)
    if cache_item:
        return None

    layer_name = f"composite_{_id_hashes}"

    archive_path, archive_hash = _make_layers_zips(
        archive_dir, layer_name, list(needed_info)
    )

    # convert to json string then back to python object because it has a Filepath type in it and that is always handled weird.
    LAYER_CACHE.add_item(_id_hashes, (archive_path, archive_hash))

    rv = DependencyLayer(cdev_name=layer_name, artifact_path=archive_path)

    return rv


def _make_layers_zips(
    zip_archive_location_directory: DirectoryPath,
    layer_name: str,
    needed_info: List[ExternalDependencyWriteInfo],
) -> Tuple[FilePath, str]:
    """Create the zip archive that will be deployed with the handler function.
    
    All modules provide are written to a single archive such that the module is in '/python/<module_name>'.

    Args:
        zip_archive_location_directory (DirectoryPath): The directory that the archive will be created in.
        layer_name (str): base name for the archive
        needed_info (List[ExternalDependencyWriteInfo]): The information about what modules to add to the archive

    Returns:
        archive_path (str): The location of the created archive relative to the Cdev project location
        hash (str): A identifying hash of the archive
    """

    _file_hashes = []
    zip_archive_full_path = os.path.join(
        zip_archive_location_directory, layer_name + ".zip"
    )
    seen_pkgs = set()

    if os.path.isfile(zip_archive_full_path):
        os.remove(zip_archive_full_path)

    for info in needed_info:
        if info.id in seen_pkgs:
            continue

        seen_pkgs.add(info.id)

        with ZipFile(zip_archive_full_path, "a") as zipfile:
            if os.path.isfile(info.location):
                # this is a single python file not a folder (ex: six.py)
                file_name = os.path.split(info.location)[1]
                # since this is a module that is just a single file plop in /python/<filename> and it will be on the pythonpath

                zipfile.write(info.location, os.path.join("python", file_name))
                _file_hashes.append(cdev_hasher.hash_file(info.location))

            else:
                pkg_name = os.path.split(info.location)[1]

                for dirname, subdirs, files in os.walk(info.location):
                    if dirname.split("/")[-1] in EXCLUDE_SUBDIRS:
                        continue

                    zip_dir_name = os.path.normpath(
                        os.path.join(
                            "python", pkg_name, os.path.relpath(dirname, info.location)
                        )
                    )

                    for filename in files:
                        original_path = os.path.join(dirname, filename)
                        zipfile.write(
                            original_path, os.path.join(zip_dir_name, filename)
                        )
                        _file_hashes.append(cdev_hasher.hash_file(original_path))

                pkg_dir = os.path.dirname(info.location)
                for obj in os.listdir(pkg_dir):
                    # Search in the general packaging directory for any other directory with the package name
                    # for example look for numpy.lib when including numpy
                    if os.path.join(pkg_dir, obj) == info.location:
                        continue

                    if (
                        os.path.isdir(os.path.join(pkg_dir, obj))
                        and obj.split(".")[0] == os.path.split(info.location)[1]
                    ):
                        for dirname, subdirs, files in os.walk(
                            os.path.join(pkg_dir, obj)
                        ):
                            if dirname.split("/")[-1] in EXCLUDE_SUBDIRS:
                                continue

                            zip_dir_name = os.path.normpath(
                                os.path.join(
                                    "python",
                                    obj,
                                    os.path.relpath(
                                        dirname, os.path.join(pkg_dir, obj)
                                    ),
                                )
                            )

                            for filename in files:
                                original_path = os.path.join(dirname, filename)
                                zipfile.write(
                                    original_path, os.path.join(zip_dir_name, filename)
                                )
                                _file_hashes.append(
                                    cdev_hasher.hash_file(original_path)
                                )

    full_archive_hash = cdev_hasher.hash_list(_file_hashes)

    return (
        zip_archive_full_path,
        full_archive_hash,
    )
