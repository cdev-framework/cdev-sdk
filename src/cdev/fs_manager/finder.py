import inspect
import importlib
import os
import sys

from cdev.cparser import cdev_parser as cparser
from cdev.fs_manager.writer import write_intermediate_files


ANNOTATION_LABEL = "lambda_function"


def _get_module_name_from_path(fp):
    return fp.split("/")[-1][:-3]


def find_serverless_function_information_from_file(fp):
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

    include_functions = [x.get("handler_name") for x in serverless_function_information]

    parsed_function_info = cparser.parse_functions_from_file(fp, include_functions=include_functions, remove_top_annotation=True)

    # return a dict<str, [(lineno)]>  that represents the parsed function and their 
    rv = {}

    for f in parsed_function_info.parsed_functions:
        rv[f.name] = f.needed_line_numbers

    return rv


def find_serverless_function_information_in_module(python_module):
    listOfFunctions = inspect.getmembers(python_module, inspect.isfunction)
    
    if not listOfFunctions:
        # print(f"No functions in {path}")
        return

    any_servless_functions = False

    for _name, func in listOfFunctions:
        if func.__qualname__.startswith(ANNOTATION_LABEL+"."):
            any_servless_functions = True

    if not any_servless_functions:
        return


    serverless_function_information = []


    for _name, func in listOfFunctions:
        if func.__qualname__.startswith(ANNOTATION_LABEL+"."):
            serverless_function_information.append(func())
            

    return serverless_function_information


def parse_folder(folder_path):
    if not os.path.isdir(folder_path):
        return None

    python_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f[-3:]==".py"]

    print(python_files)
    os.chdir(folder_path)

    for pf in python_files:
        fullfilepath = os.path.join("..",folder_path, pf)
        localpath = os.path.join(".", pf)
        print(localpath)
        rv = find_serverless_function_information_from_file(localpath)
        
        print(rv)
        
        print(localpath)
        write_intermediate_files(fullfilepath, rv)