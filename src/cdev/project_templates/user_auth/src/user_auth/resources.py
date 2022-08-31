# Generated as part of the user auth project template
import json

from cdev.aws.api import Api
from cdev.aws.lambda_function import ServerlessFunction

from cdev import Project as cdev_project

myProject = cdev_project.instance()

DemoApi = Api("demoapi")
demo_route = DemoApi.route("/demo", "GET")


@ServerlessFunction("demo_handler", events=[demo_route.event()])
def hello_world(event, context):
    print("Hello from inside your Function!")

    return {
        "status_code": 200,
        "body": json.dumps({"message": "Hello World From The Backend!"}),
        "headers": {"content-type": "application/json"},
    }


myProject.display_output("Base API URL", DemoApi.output.endpoint)
myProject.display_output("Routes", DemoApi.output.endpoints)
