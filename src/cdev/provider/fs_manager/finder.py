import inspect
import importlib
import os
import sys
from sortedcontainers.sortedlist import SortedKeyList, SortedList, identity
from typing import List



from cdev.schema import utils as cdev_schema_utils
from cdev.frontend.models import Rendered_Resource as frontend_resource
from cdev.utils import hasher

from ..cparser import cdev_parser as cparser

from ..resources.general import pre_parsed_serverless_function, parsed_serverless_function_info, parsed_serverless_function_resource

from . import utils as fs_utils
from . import writer


ANNOTATION_LABEL = "lambda_function_annotation"


def _get_module_name_from_path(fp):
    return fp.split("/")[-1][:-3]


def find_serverless_function_information_from_file(fp) -> List[parsed_serverless_function_info]:
    # Input: filepath
    if not os.path.isfile(fp):
        print("OH NO")
        return

    mod_name = _get_module_name_from_path(fp)
        
    if sys.modules.get(mod_name):
        print(f"already loaded {mod_name}")
        importlib.reload(sys.modules.get(mod_name))
        
    # When the python file is imported and executed all the Cdev resources are created and registered with the
    # singleton
    mod = importlib.import_module(mod_name)

    serverless_function_information = find_serverless_function_information_in_module(mod)

    if not serverless_function_information:
        return

    include_functions_list = [x.handler_name for x in serverless_function_information]
    include_functions_set = set(include_functions_list)

    parsed_function_info = cparser.parse_functions_from_file(fp, include_functions=include_functions_list, remove_top_annotation=True)

    handler_to_functionobj = {}
    for serverless_func in serverless_function_information:

        if serverless_func.handler_name in include_functions_set:
            handler_to_functionobj[serverless_func.handler_name] = serverless_func

    rv = []

    for parsed_function in parsed_function_info.parsed_functions:
        tmp = handler_to_functionobj.get(parsed_function.name).dict()
        tmp["needed_lines"] = parsed_function.get_line_numbers_serializeable()
        tmp["dependencies"] = list(SortedList(parsed_function.imported_packages))
        
        rv.append(parsed_serverless_function_info(**tmp))

    return rv


def find_serverless_function_information_in_module(python_module) -> List[pre_parsed_serverless_function]:
    listOfFunctions = inspect.getmembers(python_module, inspect.isfunction)
    
    if not listOfFunctions:
        return

    any_servless_functions = False

    # TODO Expand this to handle other annotation symbols
    for _name, func in listOfFunctions:

        if func.__qualname__.startswith(ANNOTATION_LABEL+"."):
            any_servless_functions = True

    if not any_servless_functions:
        return


    serverless_function_information = []


    for _name, func in listOfFunctions:
        if func.__qualname__.startswith(ANNOTATION_LABEL+"."):
            info = func()
            serverless_function_information.append(info)
            

    return serverless_function_information


def parse_folder(folder_path, prefix=None) -> List[frontend_resource]:
    if not os.path.isdir(folder_path):
        return None

    python_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f[-3:]==".py"]

    original_path = os.getcwd()
    os.chdir(folder_path)

    # [{<resource>}]
    rv = SortedKeyList(key=lambda x: x.hash)


    for pf in python_files:
        final_function_info = _generate_resources_from_file(pf, folder_path, prefix)

        if final_function_info:
            rv.update(final_function_info)

        
    os.chdir(original_path)

    return list(rv)



def _generate_resources_from_file(python_file: str, parent_folder: str, prefix) -> List[dict]:
    fullfilepath = os.path.join("..", parent_folder, python_file)
    # Direction from the current dir
    from_root_path = os.path.join(parent_folder, python_file)
    localpath = os.path.join(".", python_file)

    file_info = find_serverless_function_information_from_file(localpath)

    if not file_info:
        # TODO BAD THROW ERROR
        return 
    

    # Get the file as a list of lines so that we can get individual lines
    file_list = fs_utils.get_file_as_list(fullfilepath)


    final_function_info = []

    for function_info_obj in file_info:
        # For each function need to add info about:
        #   - Parsed Path Location -> path to parsed file loc
        #   - Source Code Hash     -> hash([line1,line2,....])
        #   - Dependencies Hash    -> hash([dep1,dep2,...])
        #   - Identity Hash        -> hash(src_code_hash, dependencies_hash)
        #   - Total Hash           -> hash(identity_hash, metadata_hash) 
        #   - Metadata Hash        -> hash(parsed_path)

        # Used keys:

        # Parsed Path
        function_info = function_info_obj.dict()



        function_info['original_path'] = fullfilepath
        function_info['parsed_path'] = fs_utils.get_parsed_path(from_root_path, function_info.get("handler_name"), prefix)

        writer.write_intermediate_file(localpath, function_info.get("needed_lines"), function_info.get("parsed_path"))

        # Join the needed lined into a string and get the md5 hash 
        function_info['source_code_hash'] = hasher.hash_list(fs_utils.get_lines_from_file_list(file_list, function_info.get('needed_lines')))


        # Hash of dependencies directly used in this function
        if function_info.get('dependencies'):
            dependencies_hash = hasher.hash_list(function_info.get('dependencies'))
        else:
            dependencies_hash = "0"
        
        function_info['dependencies_hash'] = dependencies_hash


        # Create identity hash
        function_info['identity_hash'] = hasher.hash_list([function_info['source_code_hash'], function_info['dependencies_hash']])

        # Create metadata hash
        function_info['metadata_hash'] = hasher.hash_list([function_info['parsed_path']])

        ## BASE RENDERED RESOURCE INFORMATION
        # Create the total hash
        function_info['hash'] = hasher.hash_list([function_info['identity_hash'], function_info['metadata_hash'] ])
    
        function_info['ruuid'] = "cdev::general::parsed_function"

        as_resource = parsed_serverless_function_resource(
            **function_info
        )

        final_function_info.append(as_resource)

    return final_function_info
