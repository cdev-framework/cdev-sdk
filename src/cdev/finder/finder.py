import importlib
import inspect
import os
import sys


ANNOTATION_LABEL = "lambda_function"


def find_file(base_path, pf):
    path = os.path.join(base_path, pf + ".py")
    if sys.modules.get(pf) and inspect.getfile(sys.modules.get(pf)) == path:
        print(f"already loaded {pf}")


    mod = importlib.import_module(pf)
    print("hello>>>>")
    functions = find_serverless_functions_in_module(mod, path)


def find_serverless_functions_in_module(python_module, path):
    listOfFunctions = inspect.getmembers(python_module, inspect.isfunction)
    print(listOfFunctions)

    if not listOfFunctions:
        # print(f"No functions in {path}")
        return

    any_servless_functions = False

    for _name, func in listOfFunctions:
        if func.__qualname__.startswith(ANNOTATION_LABEL+"."):
            any_servless_functions = True

    if not any_servless_functions:
        return


    serverless_functions = set()
    for _name, func in listOfFunctions:
        if func.__qualname__.startswith(ANNOTATION_LABEL+"."):
            info = func()
            name = info.get("name")
            middleware = info.get("middleware")
            print("MY FIRENDS")
            print(info)

    return serverless_functions
