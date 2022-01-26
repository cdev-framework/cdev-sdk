# Generated as part of Quick Start project template 

from cdev.resources.simple.xlambda import simple_function_annotation

@simple_function_annotation("hello_world_function")
def hello_world(event, context):
    print('Hellow World!')