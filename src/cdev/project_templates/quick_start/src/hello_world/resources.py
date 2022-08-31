# Generated as part of default project template

from cdev.aws.api import Api
from cdev.aws.lambda_function import ServerlessFunction

from cdev import Project as cdev_project

myProject = cdev_project.instance()

DemoApi = Api("demoapi")

hello_route = DemoApi.route("/hello_world", "GET")


@ServerlessFunction("hello_world_function", events=[hello_route.event()])
def hello_world(event, context):
    print("Hello from inside your Function! 👋")

    return "Hello World! 🚀"


myProject.display_output("Base API URL", DemoApi.output.endpoint)
myProject.display_output("Routes", DemoApi.output.endpoints)
