# Generated as part of Quick Start project template

from cdev.resources.simple.xlambda import simple_function_annotation

import aurora_data_api
import pandas

from .utils import helper_function


@simple_function_annotation("hello_world_function")
def hello_world(event, context):
    print("Hello from inside your Function!")
    helper_function()

    return {"status_code": 200, "message": "Hello Outside World!"}


@simple_function_annotation("hello_world_function2")
def hello_world2(event, context):
    print("Hello from inside your Function!")
    print(aurora_data_api)

    return {"status_code": 200, "message": "Hello Outside World!"}


@simple_function_annotation("hello_world_function3")
def hello_world3(event, context):
    print("Hello from inside your Function!")
    print(aurora_data_api)
    print(pandas)

    return {"status_code": 200, "message": "Hello Outside World!"}


@simple_function_annotation("hello_world_function4")
def hello_world4(event, context):

    return {"status_code": 200, "message": "Hello Outside World!"}
