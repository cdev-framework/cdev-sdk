import importlib
import os
from pydantic.main import BaseModel
from pydantic.types import FilePath
from sortedcontainers.sortedlist import SortedKeyList
import sys
from typing import Dict, List, Tuple

from core.constructs.resource import (
    Resource,
    ResourceModel,
    ResourceReferenceModel,
    Resource_Reference,
)

from core.resources.simple.xlambda import (
    DependencyLayer,
    SimpleFunction,
    function_configuration,
    simple_function_model,
)

from core.utils import hasher, module_loader, paths, logger

from serverless_parser import parser as serverless_parser


from . import utils as fs_utils
from . import writer
from . import package_mananger as cdev_package_manager

log = logger.get_cdev_logger(__name__)


ANNOTATION_LABEL = "lambda_function_annotation"


def parse_folder(
    folder_path, prefix=None
) -> Tuple[List[ResourceModel], List[ResourceReferenceModel]]:
    """
    This function takes a folder and goes through it looking for cdev resources. Specifically, it loads all available python files
    and uses the loaded module to determine the resources defined in the files. Most resources are simple, but there is extra work
    needed to handle the serverless functions. Serverless functions are parsed to optimized the actual deployed artifact using the
    cparser library.
    """
    if not os.path.isdir(folder_path):
        raise Exception

    python_files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f[-3:] == ".py"
    ]

    # [{<resource>}]
    resources_rv = SortedKeyList(key=lambda x: x.hash)

    references_rv = SortedKeyList(key=lambda x: x.hash)

    for pf in python_files:
        final_function_info = _find_resources_information_from_file(
            os.path.join(folder_path, pf)
        )
        resources = final_function_info[0]
        references = final_function_info[1]
        if resources:
            resources_rv.update(resources)

        if references:
            references_rv.update(references)


    return resources_rv, references_rv


def _get_module_name_from_path(fp):
    relative_to_project_path = paths.get_relative_to_project_path(fp)

    relative_to_project_path_parts = relative_to_project_path.split("/")

    if relative_to_project_path_parts[-1] == "__init__.py":
        relative_to_project_path_parts.pop()
    else:
        # remove the .py part of the file name
        relative_to_project_path_parts[-1] = relative_to_project_path_parts[-1][:-3]

    full_module_path_from_project = ".".join(relative_to_project_path_parts)

    return full_module_path_from_project


def _find_resources_information_from_file(
    fp: FilePath,
) -> Tuple[List[ResourceModel], List[ResourceReferenceModel]]:
    # Input: filepath
    if not os.path.isfile(fp):
        return

    mod_name = _get_module_name_from_path(fp)

   
    # When the python file is imported and executed all the Cdev resources are created
    mod = module_loader.import_module(mod_name)

    resource_rv = []
    reference_rv = []

    functions_to_parse: List[str] = []

    for i in dir(mod):
        obj = getattr(mod, i)
        if isinstance(obj, Resource):
            # Find all the Resources in the module and render them

            if isinstance(obj, SimpleFunction):
                functions_to_parse.append(obj.configuration.Handler)
                
            else:
                resource_rv.append(obj.render())

        elif isinstance(obj, Resource_Reference):
            reference_rv.append(obj.render())

    log.info(f"FUNCTIONS TO PARSE: {functions_to_parse}")
    if functions_to_parse:
        parsed_function_info = _parse_serverless_function(
            fp, functions_to_parse
        )

        
    return resource_rv, reference_rv


class parsed_serverless_function_info(BaseModel):
    src_code_hash: str
    archivepath: FilePath
    handler: str
    external_dependencies_info: List[DependencyLayer]

    def __init__(
        __pydantic_self__,
        src_code_hash: str,
        archivepath: FilePath,
        handler: str,
        external_dependencies_info: List[DependencyLayer],
    ) -> None:
        super().__init__(
            **{
                "src_code_hash": src_code_hash,
                "archivepath": archivepath,
                "handler": handler,
                "external_dependencies_info": external_dependencies_info,
            }
        )


def _parse_serverless_functions(
    filepath: FilePath,
    functions_names_to_parse: List[str],
    handler_name_to_info: Dict[str, simple_function_model],
    manual_includes: Dict = {},
    global_includes: List = [],
) -> List[simple_function_model]:

    include_functions_list = functions_names_to_parse

    parsed_file_info = serverless_parser.parse_functions_from_file(
        filepath, include_functions=include_functions_list, remove_top_annotation=True
    )

    rv = {}
    for parsed_function in parsed_file_info.parsed_functions:
        final_info = {}

        cleaned_name = _clean_function_name(parsed_function.name)
        intermediate_path = fs_utils.get_parsed_path(filepath, cleaned_name)

        print(f"imported modules ->>> {parsed_function.imported_packages}")
        needed_module_information = cdev_package_manager.get_top_level_module_info(
            parsed_function.imported_packages, filepath
        )
        print(f"Need modules infos ->>> { needed_module_information}")

        #fs_utils.print_dependency_tree(
        #    parsed_function.name, [v for k, v in needed_module_information.items()]
        #)

        (
            src_code_hash,
            archive_path,
            base_handler_path,
            dependencies_info,
        ) = writer.create_full_deployment_package(
            filepath,
            parsed_function.get_line_numbers_serializeable(),
            intermediate_path,
            needed_module_information,
        )

        handler_path = base_handler_path + "." + parsed_function.name

        previous_info = handler_name_to_info.get(parsed_function.name)

        configuration = function_configuration(
            Handler=
        )

        new_function = SimpleFunction(
            cdev_name=previous_info.name,
            filepath=paths.get_relative_to_project_path(archive_path),
            function_name=previous_info.function_name,
            events=previous_info.events,

        )

        final_info = parsed_serverless_function_info(
            src_code_hash=src_code_hash,
            archivepath=,
            handler=handler_path,
            external_dependencies_info=dependencies_info,
        )

        

        rv[cleaned_name] = final_info

    return rv


def _clean_function_name(potential_name: str) -> str:
    return potential_name.replace(" ", "_")
