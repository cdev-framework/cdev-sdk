# Generated as part of Quick Start project template
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator

from cdev.resources.simple.xlambda import simple_function_annotation


@lambda_handler_decorator
def middleware_before_after(handler, event, context):
    print(f"BEFORE")
    # logic_before_handler_execution()
    response = handler(event, context)
    # logic_after_handler_execution()
    print(f"AFTER")
    return response


@simple_function_annotation("middleware_example")
@middleware_before_after
def lambda_handler(event, context):

    print("Hello from inside your Function!")
