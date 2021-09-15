from enum import Enum
from typing import List


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher, environment as cdev_environment

from .xlambda import Event as lambda_event, EventTypes


class simple_api_model(Rendered_Resource):
    api_name: str
    routes: List[lambda_event]
    allow_cors: bool


class simple_api_output(str, Enum):
    cloud_id = "cloud_id"
    routes = "routes"


class Api(Cdev_Resource):

    def __init__(self, cdev_name: str, api_name: str, allow_cors: bool) -> None:
        super().__init__(cdev_name)
        self.api_name = f"{api_name}_{cdev_environment.get_current_environment_hash()}"
        self._routes = []
        self.allow_cors = allow_cors
        self.hash = (hasher.hash_list([hasher.hash_list(self._routes), self.api_name, self.allow_cors]))


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

        self.hash = hasher.hash_list([hasher.hash_list(self._routes), self.api_name, self.allow_cors]) 
        return event

    
    def render(self) -> simple_api_model:
        return simple_api_model(**{
            "ruuid": "cdev::simple::api",
            "name": self.name,
            "hash": self.hash,
            "api_name": self.api_name,
            "routes": self._routes,
            "allow_cors": self.allow_cors
            }
        )

    def from_output(self, key: simple_api_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"cdev::simple::api::{self.hash}", "key": key.value, "type": "cdev_output"})

