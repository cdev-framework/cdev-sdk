from cdev.resources.aws.lambda_function import lambda_function

@lambda_function("demo")
def hello_world(event,context):
    return "HELLO"


@lambda_function("demo2")
def hello_world2(event,context):
    return "HELLO"
