import inspect


ANNOTATION_LABEL = "lambda_function"


def find_serverless_function_information_in_module(python_module):
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


    serverless_function_information = []


    for _name, func in listOfFunctions:
        if func.__qualname__.startswith(ANNOTATION_LABEL+"."):
            serverless_function_information.append(func())
            
    #print(serverless_function_information)
    return serverless_function_information
