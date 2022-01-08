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

from cdev.resources.simple.xlambda import (
    DependencyLayer,
    simple_lambda,
    simple_aws_lambda_function_model,
)

from core.utils import hasher, paths, logger

from src.serverless_parser import parser as serverless_parser


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

    reference_rv = SortedKeyList(key=lambda x: x.hash)

    for pf in python_files:
        final_function_info = _find_resources_information_from_file(
            os.path.join(folder_path, pf)
        )
        if final_function_info:
            resources_rv.update(final_function_info)

    return resources_rv


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
        print("OH NO")
        return

    mod_name = _get_module_name_from_path(fp)

    print("-------")
    if sys.modules.get(mod_name):
        # print(f"already loaded {mod_name}")
        importlib.reload(sys.modules.get(mod_name))

    # When the python file is imported and executed all the Cdev resources are created
    mod = importlib.import_module(mod_name)
    print("-------")

    resource_rv = []
    reference_rv = []

    functions_to_parse = []
    function_name_to_resource_model: Dict[str, simple_aws_lambda_function_model] = {}

    for i in dir(mod):
        obj = getattr(mod, i)
        if isinstance(obj, Resource):
            # Find all the Resources in the module and render them

            log.info(f"FOUND {obj} as Resource in {mod}")

            if isinstance(obj, simple_lambda):
                log.info(f"FOUND FUNCTION TO PARSE {obj}")
                pre_parsed_info = obj.render()

                functions_to_parse.append(pre_parsed_info.configuration.Handler)
                function_name_to_resource_model[
                    pre_parsed_info.configuration.Handler
                ] = pre_parsed_info
                log.info(f"PREPROCESS {pre_parsed_info}")

            else:
                resource_rv.append(obj.render())

        elif isinstance(obj, Resource_Reference):
            reference_rv.append(obj.render())

    log.info(f"FUNCTIONS TO PARSE: {functions_to_parse}")
    if functions_to_parse:
        parsed_function_info = _create_serverless_function_resources(
            fp, functions_to_parse
        )
        log.info(parsed_function_info)

        for parsed_function_name in parsed_function_info:
            if not parsed_function_name in function_name_to_resource_model:
                log.error("ERROR UNKNOWN FUNCTION NAME RETURNED")
                raise Exception

            tmp = function_name_to_resource_model.get(parsed_function_name)
            tmp.src_code_hash = parsed_function_info.get(parsed_function_name).get(
                "src_code_hash"
            )

            if parsed_function_info.get(
                parsed_function_name
            ).external_dependencies_info:
                tmp.external_dependencies = parsed_function_info.get(
                    parsed_function_name
                ).external_dependencies_info
                tmp.external_dependencies_hash = [
                    x.render().hash
                    for x in parsed_function_info.get(
                        parsed_function_name
                    ).external_dependencies_info
                ]

                for dependency in tmp.external_dependencies:
                    reference_rv.append(dependency.render())

            else:
                tmp.external_dependencies = None
                tmp.external_dependencies_hash = None

            tmp.filepath = parsed_function_info.get(parsed_function_name).get(
                "file_path"
            )
            tmp.configuration.Handler = parsed_function_info.get(
                parsed_function_name
            ).get("Handler")

            tmp.config_hash = tmp.configuration.get_cdev_hash()

            if tmp.external_dependencies_hash:
                tmp.hash = hasher.hash_list(
                    [
                        tmp.src_code_hash,
                        tmp.config_hash,
                        tmp.events_hash,
                        tmp.permissions_hash,
                        tmp.external_dependencies_hash,
                    ]
                )
            else:
                tmp.hash = hasher.hash_list(
                    [
                        tmp.src_code_hash,
                        tmp.config_hash,
                        tmp.events_hash,
                        tmp.permissions_hash,
                    ]
                )

            log.info(f"updated to {tmp}")
            resource_rv.append(tmp)

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


def _create_serverless_function_resources(
    filepath: FilePath,
    functions_names_to_parse: List[str],
    manual_includes: Dict = {},
    global_includes: List = [],
) -> Dict[str, parsed_serverless_function_info]:

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

        fs_utils.print_dependency_tree(
            parsed_function.name, [v for k, v in needed_module_information.items()]
        )

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

        final_info = parsed_serverless_function_info(
            src_code_hash=src_code_hash,
            archivepath=paths.get_relative_to_project_path(archive_path),
            handler=handler_path,
            external_dependencies_info=dependencies_info,
        )

        rv[cleaned_name] = final_info

    return rv


def _clean_function_name(potential_name: str) -> str:
    return potential_name.replace(" ", "_")
