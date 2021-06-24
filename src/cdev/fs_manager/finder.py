import hashlib
import inspect
import importlib
import os
import sys

from cdev.cparser import cdev_parser as cparser

from . import utils as fs_utils


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

    if not serverless_function_information:
        return

    include_functions = [x.get("handler_name") for x in serverless_function_information]

    parsed_function_info = cparser.parse_functions_from_file(fp, include_functions=include_functions, remove_top_annotation=True)

    # return a [{function_name, needed_lines},...]  that represents the parsed function and their 
    rv = []

    

    for f in parsed_function_info.parsed_functions:
        rv.append({
            "function_name": f.name,
            "needed_lines": f.needed_line_numbers,
            "dependencies": f.needed_imports
        })

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


def parse_folder(folder_path, prefix=None):
    if not os.path.isdir(folder_path):
        return None

    python_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f[-3:]==".py"]

    original_path = os.getcwd()
    os.chdir(folder_path)

    # [{"filename", "function_information"}]
    rv = []

    for pf in python_files:
        fullfilepath = os.path.join("..",folder_path, pf)
        # Direction from the current dir
        from_root_path = os.path.join(folder_path, pf)
        localpath = os.path.join(".", pf)

        # rv: [{"function_name", "needed_lines", "dependencies_hash"},]
        file_info = find_serverless_function_information_from_file(localpath)

        if not file_info:
            continue
        

        # Get the file as a list of lines so that we can get individual lines
        file_list = fs_utils.get_file_as_list(fullfilepath)

    
        final_function_info = []

        for function_info in file_info:
            # For each function needed to add info about:
            #   - Parsed Path Location -> path to parsed file loc
            #   - Source Code Hash     -> hash([line1,line2,....])
            #   - Dependencies Hash    -> hash([dep1,dep2,...])
            #   - Identity Hash        -> hash(src_code_hash, dependencies_hash)
            #   - Total Hash           -> hash(identity_hash, metadata_hash) 
            #   - Metadata Hash        -> hash(parsed_path)
   
            # Parsed Path
            function_info['parsed_path'] = fs_utils.get_parsed_path(from_root_path, function_info.get("function_name"), prefix)

            # Join the needed lined into a string and get the md5 hash 
            file_as_string = ''.join(fs_utils.get_lines_from_file_list(file_list, function_info.get('needed_lines')))
            encoded_file_as_string = file_as_string.encode()
            file_hash = hashlib.md5(encoded_file_as_string).hexdigest()
            function_info['source_code_hash'] = file_hash

            # Has of dependencies
            if function_info['dependencies']:
                dependencies_hash = hashlib.md5("".join(function_info['dependencies']).encode()).hexdigest() 
            else:
                dependencies_hash = "0"
            
            function_info['dependencies_hash'] = dependencies_hash


            # Create identity hash
            joined_identity_str = "".join([function_info['source_code_hash'], function_info['dependencies_hash']])
            identity_hash = hashlib.md5(joined_identity_str.encode()).hexdigest() 
            function_info['identity_hash'] = identity_hash


            # Create metadata hash
            joined_metadata_str = "".join([function_info['parsed_path']])
            metadata_hash = hashlib.md5(joined_metadata_str.encode()).hexdigest() 
            function_info['metadata_hash'] = metadata_hash

            joined_total_str = "".join([identity_hash, metadata_hash])
            total_hash = hashlib.md5(joined_total_str.encode()).hexdigest()
            function_info['total_hash'] = total_hash
            
    
            final_function_info.append(function_info)

        
        rv.append({"filename": from_root_path, "function_information": final_function_info})

        
    os.chdir(original_path)

    return rv