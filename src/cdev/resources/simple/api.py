from enum import Enum
from typing import List


from ...constructs import Cdev_Resource
from ...models import Cloud_Output, Rendered_Resource
from ...utils import hasher, environment as cdev_environment

from .xlambda import Event as lambda_event, EventTypes

RUUID = "cdev::simple::api"


class simple_api_model(Resource):
    api_name: str
    routes: List[lambda_event]
    allow_cors: bool


class simple_api_output(str, Enum):
    cloud_id = "cloud_id"
    endpoints = "endpoints"
    endpoint = "endpoint"


class Api(Cdev_Resource):
    RUUID = "cdev::simple::api"

    def __init__(
        self, cdev_name: str, api_name: str = "", allow_cors: bool = True
    ) -> None:
        """
        Create a simple http Api.

        Args
            cdev_name (str): name of the resource
            api_name (str, optional): name in aws of the resource. defaults to cdev_name if not provided
            allow_cors (str, optional): allow CORS on the api

        Note:
            To create routes for the api use the `route` method
        """

        super().__init__(cdev_name)
        self.api_name = (
            f"{api_name}_{cdev_environment.get_current_environment_hash()}"
            if api_name
            else f"{cdev_name}_{cdev_environment.get_current_environment_hash()}"
        )
        self._routes = []
        self.allow_cors = allow_cors
        self.hash = hasher.hash_list(
            [hasher.hash_list(self._routes), self.api_name, self.allow_cors]
        )

    def route(self, path: str, verb: str) -> lambda_event:
        config = {"path": path, "verb": verb}

        event = lambda_event(
            **{
                "original_resource_name": self.name,
                "original_resource_type": self.RUUID,
                "event_type": EventTypes.HTTP_API_ENDPOINT,
                "config": config,
            }
        )

        self._routes.append(event)

        self.hash = hasher.hash_list(
            [hasher.hash_list(self._routes), self.api_name, self.allow_cors]
        )
        return event

    def render(self) -> simple_api_model:
        return simple_api_model(
            **{
                "ruuid": self.RUUID,
                "name": self.name,
                "hash": self.hash,
                "api_name": self.api_name,
                "routes": self._routes,
                "allow_cors": self.allow_cors,
            }
        )

    def from_output(self, key: simple_api_output) -> Cloud_Output:
        return Cloud_Output(
            **{
                "resource": f"{self.RUUID}::{self.hash}",
                "key": key.value,
                "type": "cdev_output",
            }
        )
