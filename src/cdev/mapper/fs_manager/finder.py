import importlib
import os
import sys
from pydantic.types import FilePath
from sortedcontainers.sortedlist import SortedKeyList
from typing import Dict, List


from cdev.constructs import Cdev_Resource
from cdev.models import Rendered_Resource

from cdev.resources.simple.xlambda import simple_lambda

from cdev.utils import hasher, paths, logger
from cdev.settings import set_setting as set_cdev_setting

from ..cparser import cdev_parser as cparser



from . import utils as fs_utils
from . import writer
from . import package_mananger as cdev_package_manager

log = logger.get_cdev_logger(__name__)


ANNOTATION_LABEL = "lambda_function_annotation"


def _get_module_name_from_path(fp):
    return fp.split("/")[-1][:-3]


def _find_resources_information_from_file(fp) -> List[Rendered_Resource]:
    # Input: filepath
    if not os.path.isfile(fp):
        print("OH NO")
        return
    set_cdev_setting("CURRENT_PARSING_DIR", os.path.dirname(fp))

    mod_name = _get_module_name_from_path(fp)
        
    if sys.modules.get(mod_name):
        #print(f"already loaded {mod_name}")
        importlib.reload(sys.modules.get(mod_name))
        
    # When the python file is imported and executed all the Cdev resources are created
    mod = importlib.import_module(mod_name)
    rv = []
    
    functions_to_parse = []
    function_name_to_rendered_resource = {}

    for i in dir(mod):
        if isinstance(getattr(mod,i), Cdev_Resource):
            # Find all the Cdev_Resources in the module and render them
            obj = getattr(mod,i)
            log.info(f"FOUND {obj} as Cdev_Resource in {mod}")

            if isinstance(obj, simple_lambda):
                log.info(f"FOUND FUNCTION TO PARSE {obj}")
                pre_parsed_info = obj.render()

                functions_to_parse.append(pre_parsed_info.configuration.Handler)
                function_name_to_rendered_resource[_clean_function_name(pre_parsed_info.configuration.Handler)] = pre_parsed_info
                log.info(f"PREPROCESS {pre_parsed_info}")

            else:
                rv.append(obj.render())

    log.info(f"FUNCTIONS TO PARSE: {functions_to_parse}")
    if functions_to_parse:
        parsed_function_info = _create_serverless_function_resources(fp, functions_to_parse)
        log.info(parsed_function_info)

        for parsed_function_name in parsed_function_info:
            if not parsed_function_name in function_name_to_rendered_resource:
                log.error("ERROR UNKNOWN FUNCTION NAME RETURNED")
                raise Exception

            tmp = function_name_to_rendered_resource.get(parsed_function_name)
            tmp.src_code_hash = parsed_function_info.get(parsed_function_name).get("src_code_hash")
            

            tmp.dependencies_info = parsed_function_info.get(parsed_function_name).get("dependencies_info")
            tmp.dependencies_hash = parsed_function_info.get(parsed_function_name).get("dependencies_hash")

            tmp.filepath =  parsed_function_info.get(parsed_function_name).get("file_path")
            tmp.configuration.Handler = parsed_function_info.get(parsed_function_name).get("Handler")
            

            tmp.config_hash = tmp.configuration.get_cdev_hash()
            
            if tmp.dependencies_hash:
                tmp.hash = hasher.hash_list([tmp.src_code_hash, tmp.config_hash, tmp.events_hash, tmp.permissions_hash, tmp.dependencies_hash])
            else:
                tmp.hash = hasher.hash_list([tmp.src_code_hash, tmp.config_hash, tmp.events_hash, tmp.permissions_hash])


            log.info(f"updated to {tmp}")
            rv.append(tmp)

    return rv


def _create_serverless_function_resources(filepath: FilePath, functions_names_to_parse: List[str], manual_includes: Dict = {}, global_includes: List = [] ) -> Dict:


    include_functions_list = functions_names_to_parse

    parsed_file_info = cparser.parse_functions_from_file(filepath, include_functions=include_functions_list, remove_top_annotation=True)

    rv = {}
    for parsed_function in parsed_file_info.parsed_functions:
        final_info = {}
        
        cleaned_name = _clean_function_name(parsed_function.name)
        intermediate_path = fs_utils.get_parsed_path(filepath, cleaned_name)
        
        
        src_code_hash, archive_path, base_handler_path, dependencies_info, dependencies_hash = writer.create_full_deployment_package(filepath, 
                                                                                parsed_function.get_line_numbers_serializeable(), 
                                                                                intermediate_path, parsed_function.needed_imports)
        
        final_handler_path = base_handler_path + "." + parsed_function.name
                    
        final_info["src_code_hash"] = src_code_hash
        final_info["file_path"] = paths.get_relative_to_project_path(archive_path)
        final_info["Handler"] = final_handler_path

        if dependencies_info:
            final_info['dependencies_info'] = dependencies_info
            final_info['dependencies_hash'] = dependencies_hash
        else:
            final_info['dependencies_info'] = []
            final_info['dependencies_hash'] = None
        
        rv[cleaned_name] = final_info

    return rv


def _clean_function_name(potential_name: str) -> str:
    return potential_name.replace(" ", "_")



def parse_folder(folder_path, prefix=None) -> List[Rendered_Resource]:
    """
    This function takes a folder and goes through it looking for cdev resources. Specifically, it loads all available python files
    and uses the loaded module to determine the resources defined in the files. Most resources are simple, but there is extra work
    needed to handle the serverless functions. Serverless functions are parsed to optimized the actual deployed artifact using the 
    cparser library.
    """
    if not os.path.isdir(folder_path):
        return None

    python_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f[-3:]==".py"]

    original_path = os.getcwd()

    os.chdir(folder_path)

    sys.path.append(os.getcwd())

    # [{<resource>}]
    rv = SortedKeyList(key=lambda x: x.hash)


    for pf in python_files:
        final_function_info = _find_resources_information_from_file(os.path.join(os.getcwd(),pf))
        if final_function_info:
            rv.update(final_function_info)

        
    os.chdir(original_path)

    return list(rv)
