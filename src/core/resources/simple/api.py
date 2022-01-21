from enum import Enum
from typing import List, FrozenSet

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher

from .events import Event, event_model, EventTypes


RUUID = "cdev::simple::api"


class route_event_model(event_model):
    path: str
    verb: str


class RouteEvent(Event):

    def __init__(self, resource_name: str, path: str, verb: str) -> None:
        self.resource_name = resource_name
        self.path = path
        self.verb = verb

    def get_hash(self) -> str:
        return hasher.hash_list([self.path, self.verb])

    def render(self) -> event_model:
        return route_event_model(
            original_resource_name= self.resource_name,
            original_resource_type= Api.RUUID ,
            event_type= EventTypes.HTTP_API_ENDPOINT,
            path=self.path,
            verb=self.verb   
        )

class simple_api_model(ResourceModel):
    routes: FrozenSet[route_event_model]
    allow_cors: bool


class simple_api_output(str, Enum):
    cloud_id = "cloud_id"
    endpoints = "endpoints"
    endpoint = "endpoint"


class Api(Resource):
    RUUID = "cdev::simple::api"

    def __init__(
        self, cdev_name: str, allow_cors: bool = True, _nonce: str = "",
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
        self._routes: List[RouteEvent] = []

        self.allow_cors = allow_cors

        self._nonce = _nonce

        self.hash = hasher.hash_list(
            [hasher.hash_list(self._routes), self.allow_cors, self._nonce]
        )

    def route(self, path: str, verb: str) -> RouteEvent:
    
        event = RouteEvent(
            self.name,
            path, 
            verb
        )

        self._routes.append(event)

        self.hash = hasher.hash_list(
            [hasher.hash_list([x.get_hash() for x in self._routes]), self.allow_cors]
        )

        return event

    def render(self) -> simple_api_model:
        routes =  frozenset(self._routes)
        
        return simple_api_model(
            **{
                "ruuid": self.RUUID,
                "name": self.name,
                "hash": self.hash,
                "routes": frozenset([x.render() for x in routes]),
                "allow_cors": self.allow_cors,
            }
        )

    def from_output(self, key: simple_api_output) -> Cloud_Output:
        return super().from_output(key)
