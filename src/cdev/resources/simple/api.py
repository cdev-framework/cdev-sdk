from enum import Enum
from typing import List


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher

from .xlambda import Event as lambda_event, EventTypes


class simple_api_model(Rendered_Resource):
    api_name: str
    routes: List[lambda_event]




class Api(Cdev_Resource):

    def __init__(self, cdev_name: str, api_name: str) -> None:
        super().__init__(cdev_name)
        self.api_name = api_name
        self._routes = []


    def route(self, path: str, verb: str) -> lambda_event:
        config = {
            "path": path,
            "verb": verb
        }


        event = lambda_event(**{
            "original_resource_name": self.name,
            "original_resource_type": "cdev::simple::api",
            "event_type": EventTypes.HTTP_API_ENDPOINT,
            "config": config
            }
        )

        self._routes.append(event)
        return event

    
    def render(self) -> simple_api_model:
        return simple_api_model(**{
            "ruuid": "cdev::simple::api",
            "name": self.name,
            "hash": hasher.hash_list([hasher.hash_list(self._routes), self.api_name]),
            "api_name": self.api_name,
            "routes": self._routes
            }
        )





class simple_api_output(str, Enum):
    cloud_id = "cloud_id"

    routes = "routes"