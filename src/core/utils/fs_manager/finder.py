from logging import raiseExceptions
import os
from pydantic import DirectoryPath
from pydantic.types import FilePath
from sortedcontainers.sortedlist import SortedKeyList
from typing import Dict, List, Tuple

from core.constructs.resource import (
    Resource,
    ResourceModel,
    ResourceReferenceModel,
    Resource_Reference,
)
from core.constructs.workspace import Workspace

from core.default.resources.simple.xlambda import (
    DependencyLayer,
    SimpleFunction,
    simple_function_model,
    SimpleFunctionConfiguration
)

from core.utils import hasher, module_loader, paths
from core.utils.logger import log

from serverless_parser import parser as serverless_parser


from . import writer
from . import package_mananger 


LAMBDA_LAYER_RUUID = "cdev::simple::lambda_layer"

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
        
        if i+1 >= len(resources):
            break

        if (resources[i].hash == resources[i+1].hash) and (resources[i].ruuid == resources[i+1].ruuid) and (resources[i].name == resources[i+1].name):
            remove_indexes.add(i)
            
    return [x for i,x in enumerate(resources) if not i in remove_indexes]

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

    if not fp[-3:] == '.py':
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
            fp, 
            functions_to_parse,
            handler_name_to_info=function_name_to_info
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
) -> Tuple[List[simple_function_model], List[DependencyLayer]]:
    """Parse a given set of function names from a given file

    Args:
        filepath (FilePath): The original file
        functions_names_to_parse (List[str]): functions to parse
        handler_name_to_info (Dict[str, SimpleFunction]): dict of additional information 
        manual_includes (Dict, optional): Dict of information about extra lines to include. Defaults to {}.
        global_includes (List, optional): List of global lines to include. Defaults to [].

    Returns:
        Tuple[List[simple_function_model], List[DependencyLayer]]: Functions and Dependencies parsed

    Use the `serverless_parser` library to get information about each desired function and its dependencies.
    Then use that information to create the needed archives for the functions and return the information as
    Resources.
    """

    # Get all the info about a set of functions from the original file
    parsed_file_info = serverless_parser.parse_functions_from_file(
        filepath, include_functions=functions_names_to_parse, remove_top_annotation=True
    )

    # Base path that the all the archives will go 
    base_archive_path = os.path.join(
        Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION,
        Workspace.instance().get_resource_state_uuid(),
    )

    if not os.path.isdir(base_archive_path):
        os.mkdir(base_archive_path)

    if Workspace.instance().settings.USE_DOCKER:
        # IF the user has denoted that they want to use Docker to build dependencies for 
        # other architectures, then make sure a downloads cache is set up
        download_cache = os.path.join(
            Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION,
            ".download_cache",
        )

        if not os.path.isdir(download_cache):
            os.mkdir(download_cache)

    else:
        download_cache = None
    
    rv = []
    seen_layers = {}

    for parsed_function in parsed_file_info.parsed_functions:

        previous_info = handler_name_to_info.get(parsed_function.name)
        needed_module_information = package_mananger.get_top_level_module_info(
            parsed_function.imported_packages, filepath, previous_info.platform, download_cache
        )

        log.debug("Needed modules (%s) for %s", needed_module_information, parsed_function.name)

        (
            handler_archive_path,
            handler_archive_hash,
            base_handler_path,
            dependencies_info,
        ) = writer.create_full_deployment_package(
            filepath,
            parsed_function.get_line_numbers_serializeable(),
            parsed_function.name,
            base_archive_path,
            pkgs=needed_module_information,
        )
        
        
        # Update the seen packages 
        if dependencies_info:
            # Helps return only one copy of each layer for the file
            # change the path of the artifact to a relative path to the workspace
            for dependency in dependencies_info:
                dependency.artifact_path = paths.get_relative_to_workspace_path(dependency.artifact_path)

            seen_layers.update(
              {x.hash:x.render() for x in dependencies_info}
            )

        handler_path = base_handler_path + "." + parsed_function.name

        new_configuration = SimpleFunctionConfiguration(
            handler=handler_path,
            description=previous_info.configuration.description,
            environment_variables=previous_info.configuration.environment_variables
        )

        new_function = SimpleFunction(
            cdev_name=previous_info.name,
            filepath=paths.get_relative_to_workspace_path(handler_archive_path),
            events=previous_info.events,
            configuration=new_configuration,
            function_permissions=previous_info.granted_permissions,
            external_dependencies=dependencies_info if dependencies_info else [],
            src_code_hash=handler_archive_hash,
            nonce=previous_info.nonce,
            platform=previous_info.platform
        )

    
        rv.append(new_function.render())

    return rv, [layer for _,layer in seen_layers.items()]
