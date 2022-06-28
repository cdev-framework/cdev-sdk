from aws_lambda_powertools.utilities.data_classes import (
    event_source,
    APIGatewayProxyEventV2,
)


from cdev.resources.simple.api import Api
from cdev.resources.simple.xlambda import simple_function_annotation

from cdev import Project as cdev_project

myProject = cdev_project.instance()

DemoApi = Api("demoapi")

hello_route = DemoApi.route("/helloworld", "GET")


@simple_function_annotation("dataclass_example", events=[hello_route.event()], tags={"environment": "dev", "sample_tag": "handler"})
@event_source(data_class=APIGatewayProxyEventV2)
def lambda_handler(event: APIGatewayProxyEventV2, context):
    if "helloworld" in event.path and event.http_method == "GET":
        print("Made it here!")
