import os
from pydantic import DirectoryPath
from pydantic.types import FilePath
from sortedcontainers.sortedlist import SortedKeyList
from typing import Dict, List, Set, Tuple, Union
from functools import partial

from core.constructs.resource import (
    Resource,
    ResourceModel,
    ResourceReferenceModel,
    Resource_Reference,
)
from core.constructs.workspace import Workspace

from core.default.resources.simple.xlambda import (
    DependencyLayer,
    DeployedLayer,
    SimpleFunction,
    dependency_layer_model,
    simple_function_model,
)

from core.utils import module_loader, paths
from core.utils.logger import log

from serverless_parser import parser as serverless_parser

import pkg_resources

from core.utils.fs_manager import (
    package_manager,
    handler_optimizer,
    package_optimizer,
    serverless_function_optimizer,
)

from .utils import _compress_lines

LAMBDA_LAYER_RUUID = "cdev::simple::lambda_layer"

COMPUTED_ENVIRONMENT_INFORMATION = None


def parse_folder(
    folder_path: DirectoryPath,
) -> Tuple[List[ResourceModel], List[ResourceReferenceModel]]:
    """Search through the given folder looking for resource and references in Python files.

    Args:
        folder_path (DirectoryPath): The directory to parse

    Returns:
        Tuple[
            List[ResourceModel],
            List[ResourceReferenceModel]
        ]

    Specifically, it loads all available python files and uses the loaded module to determine
    the resources defined in the files. Any resource or reference defined in the global
    context of the file will be detected.

    Most resources are passed back as is, but there are optimizations performed on the `simple functions`.
    Namely, Serverless functions are parsed to optimized the actual deployed artifact using the
    cparser library and then have their dependencies managed also.
    """
    if not os.path.isdir(folder_path):
        raise Exception

    log.debug("Finding resources in folder %s", folder_path)

    python_files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f[-3:] == ".py"
    ]

    # [{<resource>}]
    resources_rv = SortedKeyList(key=lambda x: x.hash)
    references_rv = SortedKeyList(key=lambda x: x.hash)

    for pf in python_files:
        found_resources, found_references = _find_resources_information_from_file(
            os.path.join(folder_path, pf)
        )

        if found_resources:
            resources_rv.update(found_resources)

        if found_references:
            references_rv.update(found_references)

    # Any duplicate layers can be removed
    cleaned_resources_rv = _deduplicate_resources_list(resources_rv)

    return cleaned_resources_rv, references_rv


def _deduplicate_resources_list(resources: List[Resource]) -> List[Resource]:
    """Remove duplicated layer resources

    Args:
        resources (List[Resource]): Sorted List of resources by x.hash

    Returns:
        resource (List[Resources]): List with duplicate resources removed

    Since multiple functions can produce the same Layer resource by referencing the same
    3rd party resource, we need to deduplicate the layers from the list.
    """
    remove_indexes = set()
    for i in range(len(resources)):

        if i + 1 >= len(resources):
            break

        if (
            (resources[i].hash == resources[i + 1].hash)
            and (resources[i].ruuid == resources[i + 1].ruuid)
            and (resources[i].name == resources[i + 1].name)
        ):
            remove_indexes.add(i)

    return [x for i, x in enumerate(resources) if not i in remove_indexes]


def _get_module_name_from_path(fp: FilePath):
    """Convert a full file path of a python path into a importable module name

    Args:
        fp (FilePath): path to file

    Returns:
        str: The importable python module name


    All module names will end up being relative to the workspace path. Note that this means
    the `Workspace` base path should be on the `Python Path`. This usually happens by default
    because the `Workspace` starts from the cwd.
    """
    relative_to_project_path = paths.get_relative_to_workspace_path(fp)

    relative_to_project_path_parts = relative_to_project_path.split("/")

    # If the last part of the file is __init__.pt then python will import it when the
    # rest of the path is given without the last part
    if relative_to_project_path_parts[-1] == "__init__.py":
        relative_to_project_path_parts.pop()
    else:
        # remove the .py part of the file name
        relative_to_project_path_parts[-1] = relative_to_project_path_parts[-1][:-3]

    # join the parts back with '.' to create the valid python module name
    full_module_path_from_project = ".".join(relative_to_project_path_parts)

    return full_module_path_from_project


def _find_resources_information_from_file(
    fp: FilePath,
) -> Tuple[List[ResourceModel], List[ResourceReferenceModel]]:
    """Load a file and find top level objects that are Resources or References

    Args:
        fp (FilePath): path to python file

    Raises:
        Exception: [description]

    Returns:
        Tuple[List[ResourceModel], List[ResourceReferenceModel]]: Resources and References
    """
    # Input: filepath
    if not os.path.isfile(fp):
        raise Exception

    if not fp[-3:] == ".py":
        raise Exception

    mod_name = _get_module_name_from_path(fp)

    # When the python file is imported and executed all the Cdev resources are created
    mod = module_loader.import_module(mod_name)

    resource_rv = []
    reference_rv = []

    functions_to_parse: List[str] = []
    function_name_to_info: Dict[str, simple_function_model] = {}

    for i in dir(mod):
        obj = getattr(mod, i)

        if isinstance(obj, Resource):
            # Find all the Resources in the module and render them

            if isinstance(obj, SimpleFunction):
                # Functions are a special case as they will go through the parser and the output
                # of that will be the returned resource
                functions_to_parse.append(obj.configuration.handler)
                function_name_to_info[obj.configuration.handler] = obj

            else:
                resource_rv.append(obj.render())

        elif isinstance(obj, Resource_Reference):
            reference_rv.append(obj.render())

    if functions_to_parse:
        log.debug("Parsing functions (%s) from %s", functions_to_parse, fp)
        parsed_function_info, parsed_dependency_info = _parse_serverless_functions(
            fp, functions_to_parse, handler_name_to_info=function_name_to_info
        )

        resource_rv.extend(parsed_function_info)
        resource_rv.extend(parsed_dependency_info)

    return resource_rv, reference_rv


def _parse_serverless_functions(
    filepath: FilePath,
    functions_names_to_parse: List[str],
    handler_name_to_info: Dict[str, SimpleFunction],
    manual_includes: Dict = {},
    global_includes: List = [],
) -> Tuple[List[simple_function_model], List[dependency_layer_model]]:
    """Parse a given set of function names from a given file

    Args:
        filepath (FilePath): The original file
        functions_names_to_parse (List[str]): functions to parse
        handler_name_to_info (Dict[str, SimpleFunction]): dict of additional information
        manual_includes (Dict, optional): Dict of information about extra lines to include. Defaults to {}.
        global_includes (List, optional): List of global lines to include. Defaults to [].

    Returns:
        Tuple[
            List[simple_function_model],
            List[DependencyLayer]
        ]: Functions and Dependencies parsed

    Use the `serverless_parser` library to get information about each desired function and its dependencies.
    Then use that information to create the needed archives for the functions and return the information as
    Resources.
    """
    full_file_path = paths.get_full_path_from_workspace_base(filepath)
    excludes = {"__pycache__"}

    (
        std_lib,
        modules_name_to_location,
        pkg_module_dependency_info,
    ) = _load_environment_information()

    # Return Values
    rv_functions: List[SimpleFunction] = []
    rv_layers: List[DependencyLayer] = []

    # Base path that the all the archives will go
    base_archive_path = os.path.join(
        Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION,
        Workspace.instance().get_resource_state_uuid(),
    )

    if not os.path.isdir(base_archive_path):
        os.mkdir(base_archive_path)

    # Caches
    packaged_module_cache = package_optimizer.load_packaged_artifact_cache(
        Workspace.instance().settings.CACHE_DIRECTORY
    )

    # Get all the info about a set of functions from the original file
    parsed_file_info = serverless_parser.parse_functions_from_file(
        full_file_path,
        include_functions=functions_names_to_parse,
        remove_top_annotation=True,
    )

    mod_creator = partial(
        package_manager.create_all_module_info,
        start_location=full_file_path,
        standard_library=std_lib,
        pkg_dependencies_data=pkg_module_dependency_info,
        pkg_locations=modules_name_to_location,
    )

    for parsed_function in parsed_file_info.parsed_functions:

        previous_info = handler_name_to_info.get(parsed_function.name)

        flattened_needed_lines = _compress_lines(parsed_function.needed_line_numbers)

        # First handle getting all the module information for this function

        handler_packager = partial(
            handler_optimizer.create_optimized_handler_artifact,
            base_packaging_path=os.getcwd(),
            intermediate_path=base_archive_path,
            needed_lines=flattened_needed_lines,
            suffix=f"_{previous_info.name}",
            excludes=excludes,
        )

        packaged_module_packager = partial(
            package_optimizer.create_packaged_module_artifacts,
            pkged_module_dependencies_data=pkg_module_dependency_info,
            base_output_directory=base_archive_path,
            exclude_subdirectories=excludes,
            created_artifact_cache=packaged_module_cache,
        )

        (
            source_artifact_path,
            source_hash,
            dependencies_info,
        ) = serverless_function_optimizer.create_optimized_serverless_function_artifacts(
            original_file_location=full_file_path,
            imported_modules=parsed_function.imported_packages,
            module_creator=mod_creator,
            handler_packager=handler_packager,
            packaged_module_optimizer=packaged_module_packager,
            additional_handler_files_directories=[],
        )

        dependencies_resources = [
            _create_layer(_create_layer_name_from_artifact_path(x[0]), x[0], x[1])
            for x in dependencies_info
        ]

        function_resource = _create_new_function(
            previous_info, source_artifact_path, source_hash, dependencies_resources
        )

        rv_functions.append(function_resource)
        rv_layers.extend(dependencies_resources)

    # dump cache
    packaged_module_cache.dump_to_file()

    return [x.render() for x in rv_functions], [x.render() for x in rv_layers]


def _load_environment_information() -> Tuple[
    Set[str], Dict[str, Tuple[FilePath, str]], Dict[str, Set[str]]
]:
    """Load information about the current packages and std library available in the environment

    Returns:
        Tuple[Set[str], Dict[str, Tuple[FilePath, str]], Dict[str, Set[str]]]: std_lib, modules_name_to_location, pkg_module_dependency_info
    """
    global COMPUTED_ENVIRONMENT_INFORMATION

    if COMPUTED_ENVIRONMENT_INFORMATION:
        return COMPUTED_ENVIRONMENT_INFORMATION

    std_lib = package_manager.get_standard_library_modules()
    modules_name_to_location = package_manager.get_packaged_modules_name_location_tag(
        pkg_resources.working_set
    )
    pkg_module_dependency_info = package_manager.create_packaged_module_dependencies(
        pkg_resources.working_set
    )

    COMPUTED_ENVIRONMENT_INFORMATION = (
        std_lib,
        modules_name_to_location,
        pkg_module_dependency_info,
    )
    return COMPUTED_ENVIRONMENT_INFORMATION


def _create_layer_name_from_artifact_path(artifact_path: FilePath) -> str:
    return str(artifact_path).split("/")[-1][:-4]


def _create_layer(
    name: str, artifact_path: FilePath, artifact_hash: str
) -> DependencyLayer:
    return DependencyLayer(
        cdev_name=name, artifact_path=artifact_path, artifact_hash=artifact_hash
    )


def _create_new_function(
    previous_info: SimpleFunction,
    new_source_artifact: FilePath,
    new_source_hash: str,
    new_dependencies: List[Union[DeployedLayer, DependencyLayer]],
) -> SimpleFunction:
    return SimpleFunction(
        cdev_name=previous_info.name,
        filepath=new_source_artifact,
        events=previous_info.events,
        configuration=previous_info.configuration,
        function_permissions=previous_info.granted_permissions,
        external_dependencies=new_dependencies,
        src_code_hash=new_source_hash,
        nonce=previous_info.nonce,
        preserve_function=previous_info._preserved_function,
        platform=previous_info.platform,
    )
