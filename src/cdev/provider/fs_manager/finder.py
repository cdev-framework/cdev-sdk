import inspect
import importlib
import os
import sys
from sortedcontainers.sortedlist import SortedKeyList, SortedList
from typing import List


from cdev.frontend.constructs import Cdev_Resource
from cdev.frontend.models import Rendered_Resource as frontend_resource
from cdev.utils import hasher

from ..cparser import cdev_parser as cparser

from ..resources.aws.lambda_function import pre_parsed_serverless_function, parsed_serverless_function_info, parsed_serverless_function_resource

from . import utils as fs_utils
from . import writer


ANNOTATION_LABEL = "lambda_function_annotation"


def _get_module_name_from_path(fp):
    return fp.split("/")[-1][:-3]


def _find_resources_information_from_file(fp) -> List[frontend_resource]:
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

    rv = []

    info = _create_serverless_function_resources(mod, fp)
    if info:
        rv.extend(info)
    

    for i in dir(mod):
        if isinstance(getattr(mod,i), Cdev_Resource):
            # Find all the Cdev_Resources in the module and render them
            obj = getattr(mod,i)
            rv.append(obj.render())

    return rv


def _create_serverless_function_resources(mod, fp) -> List[parsed_serverless_function_resource]:
    serverless_function_information = _find_serverless_function_information_in_module(mod)

    if not serverless_function_information:
        return

    include_functions_list = [x.handler_name for x in serverless_function_information]
    include_functions_set = set(include_functions_list)

    parsed_function_info = cparser.parse_functions_from_file(fp, include_functions=include_functions_list, remove_top_annotation=True)

    handler_to_functionobj = {}
    for serverless_func in serverless_function_information:

        if serverless_func.handler_name in include_functions_set:
            handler_to_functionobj[serverless_func.handler_name] = serverless_func

    function_info = []

    for parsed_function in parsed_function_info.parsed_functions:
        tmp = handler_to_functionobj.get(parsed_function.name).dict()
        tmp["needed_lines"] = parsed_function.get_line_numbers_serializeable()
        tmp["dependencies"] = list(SortedList(parsed_function.imported_packages))
        
        function_info.append(parsed_serverless_function_info(**tmp))

    # Get the file as a list of lines so that we can get individual lines
    file_list = fs_utils.get_file_as_list(fp)
    rv = []
    for function_info_obj in function_info:
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

        function_info['original_path'] = fp
        function_info['parsed_path'] = fs_utils.get_parsed_path(fp, function_info.get("handler_name"))

        writer.write_intermediate_file(fp, function_info.get("needed_lines"), function_info.get("parsed_path"))

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

        rv.append(as_resource)

    return rv

    


def _find_serverless_function_information_in_module(python_module) -> List[pre_parsed_serverless_function]:
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
        #print(final_function_info)
        if final_function_info:
            rv.update(final_function_info)

        
    os.chdir(original_path)

    return list(rv)
