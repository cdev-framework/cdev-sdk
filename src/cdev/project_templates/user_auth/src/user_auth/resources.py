# Generated as part of the User Auth project template
import json

from cdev.resources.simple.api import Api
from cdev.resources.simple.xlambda import simple_function_annotation

from cdev import Project as cdev_project

myProject = cdev_project.instance()

DemoApi = Api("demoapi")
demo_route = DemoApi.route("/demo", "GET")


@simple_function_annotation("demo_handler", events=[demo_route.event()])
def hello_world(event, context):
    print("Hello from inside your Function!")

    return {
        "status_code": 200,
        "body": json.dumps({"message": "Hello World From The Backend!"}),
        "headers": {"content-type": "application/json"},
    }


myProject.display_output("Base API URL", DemoApi.output.endpoint)
myProject.display_output("Routes", DemoApi.output.endpoints)
