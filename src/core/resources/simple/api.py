from enum import Enum
from typing import List, FrozenSet

from core.constructs.resource import Resource, ResourceModel, Cloud_Output, update_hash
from core.utils import hasher

from core.resources.simple import events


RUUID = "cdev::simple::api"


class route_event_model(events.event_model):
    path: str
    verb: str


class RouteEvent(events.Event):

    def __init__(self, resource_name: str, path: str, verb: str) -> None:
        self.resource_name = resource_name
        self.path = path
        self.verb = verb

    def get_hash(self) -> str:
        return hasher.hash_list([self.path, self.verb])

    def render(self) -> events.event_model:
        return route_event_model(
            original_resource_name= self.resource_name,
            original_resource_type= RUUID ,
            event_type= events.EventTypes.HTTP_API_ENDPOINT,
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
    """Simple HTTP Api that can be produce events.

    Args:
        Resource ([type]): [description]

    
    """

    @update_hash
    def __init__(
        self, cdev_name: str, allow_cors: bool = True, nonce: str = "",
    ):
        """Create a simple http Api.

        Args
            cdev_name (str): Name for the resource.
            allow_cors (bool, Default: True): Allow Cross Origin Resource Sharing (CORS) on the api. 

        Note:
            To create routes for the api use the `route` method
        """

        super().__init__(cdev_name, RUUID, nonce)
        
        self._allow_cors = allow_cors
        self._routes: List[RouteEvent] = []

    @property
    def allow_cors(self):
        return self._allow_cors

    @allow_cors.setter
    @update_hash
    def allow_cors(self, value: bool):
        self._allow_cors = value

    @update_hash
    def route(self, path: str, verb: str) -> RouteEvent:
    
        event = RouteEvent(
            self.name,
            path, 
            verb
        )

        self._routes.append(event)

        return event

    def compute_hash(self):
        self._hash = hasher.hash_list(
            [
                hasher.hash_list([x.get_hash() for x in self._routes]),
                self.allow_cors, 
                self.nonce
            ]
        )

    def render(self) -> simple_api_model:
        routes =  frozenset(self._routes)
        
        return simple_api_model(
            ruuid=self.ruuid,
            name=self.name,
            hash=self.hash,
            routes=frozenset([x.render() for x in routes]),
            allow_cors=self.allow_cors,
        )

    def from_output(self, key: simple_api_output) -> Cloud_Output:
        return super().from_output(key)
