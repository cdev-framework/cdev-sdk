import inspect
import importlib
import os
import sys

from cdev.cparser import cdev_parser as cparser


ANNOTATION_LABEL = "lambda_function"


def _get_module_name_from_path(fp):
    return fp.split("/")[-1][:-3]


def find_serverless_function_information_from_file(fp):
    # Input: filepath
    if not os.path.isfile(fp):
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

    print(parsed_function_info)

    # return a dict<str, [(lineno)]>  that represents the parsed function and their 
    rv = {}

    for f in parsed_function_info.parsed_functions:
        print(f"{f.name} {f.needed_line_numbers} {f.imported_packages}")
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
