from enum import Enum
from typing import List, FrozenSet
from types import MappingProxyType


from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher
from core.utils.types import FrozenDict

from .xlambda import Event as lambda_event, EventTypes


RUUID = "cdev::simple::api"


class simple_api_model(ResourceModel):
    api_name: str
    routes: FrozenSet[lambda_event]
    allow_cors: bool

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data 
        frozen = True


class simple_api_output(str, Enum):
    cloud_id = "cloud_id"
    endpoints = "endpoints"
    endpoint = "endpoint"


class Api(Resource):
    RUUID = "cdev::simple::api"

    def __init__(
        self, cdev_name: str, api_name: str = "", allow_cors: bool = True
    ) -> None:
        """
        Create a simple http Api.

        Args
            cdev_name (str): Name of the resource
            api_name (str, optional): The base name of the resource when deployed in the cloud.
            allow_cors (bool, optional): allow CORS on the api

        Note:
            To create routes for the api use the `route` method
        """

        super().__init__(cdev_name)
        self.api_name = (
            api_name
            if api_name
            else f"cdevapi"
        )
        self._routes = []
        self.allow_cors = allow_cors
        self.hash = hasher.hash_list(
            [hasher.hash_list(self._routes), self.api_name, self.allow_cors]
        )

    def route(self, path: str, verb: str) -> lambda_event:
        config = FrozenDict({"path": path, "verb": verb})
        print(f"config {config}")
        
        event = lambda_event(
            **{
                "original_resource_name": self.name,
                "original_resource_type": self.RUUID,
                "event_type": EventTypes.HTTP_API_ENDPOINT,
                "config2": config,
            }
        )

        print(event)

        self._routes.append(event)

        self.hash = hasher.hash_list(
            [hasher.hash_list(self._routes), self.api_name, self.allow_cors]
        )

        print(self._routes)
        return event

    def render(self) -> simple_api_model:
        routes =  frozenset(self._routes)
        print(routes)
        return simple_api_model(
            **{
                "ruuid": self.RUUID,
                "name": self.name,
                "hash": self.hash,
                "api_name": self.api_name,
                "routes": routes,
                "allow_cors": self.allow_cors,
            }
        )

    def from_output(self, key: simple_api_output) -> Cloud_Output:
        return super().from_output(key)
