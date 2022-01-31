from enum import Enum
from typing import Any, List, FrozenSet
from core.constructs.models import ImmutableModel
from core.constructs.output import Cloud_Output_Mapping, Cloud_Output_Sequence, Cloud_Output_Str, OutputType

from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs
from core.constructs.types import cdev_str_model
from core.utils import hasher

from core.resources.simple import events


RUUID = "cdev::simple::api"

"""

"""


########################
##### Route
########################
class route_model(ImmutableModel):
    path: str
    verb: str

class Route():
    def __init__(self, api_name: str, path: str, verb: str) -> None:
        self.api_name = api_name
        self.path = path
        self.verb = verb
       
    def hash(self) -> str:
        return hasher.hash_list([self.path, self.verb])

    def render(self) -> route_model:
        return route_model(
            path=self.path,
            verb=self.verb,
        )


    def event(self) -> 'RouteEvent':
        return RouteEvent(
            resource_name=self.api_name,
            path=self.path,
            verb=self.verb
        )

class route_event_model(events.event_model):
    path: str
    verb: str
    api_id: cdev_str_model
    route_id: cdev_str_model


class RouteEvent():

    def __init__(self, resource_name: str, path: str, verb: str) -> None:
        self.resource_name = resource_name
        self.path = path
        self.verb = verb
        self.api_id = Cloud_Output_Str(
                name=resource_name, 
                ruuid=RUUID, 
                key='cloud_id',
                type=OutputType.RESOURCE 
            )
        self.route_id = Cloud_Output_Mapping[Cloud_Output_Str](
                name=resource_name, 
                ruuid=RUUID, 
                key='endpoints',
                type=OutputType.RESOURCE,
                _member_class=Cloud_Output_Str
            )[f'{self.path} {self.verb}']

    def hash(self) -> str:
        return hasher.hash_list([self.resource_name, self.path, self.verb])

    def render(self) -> route_event_model:
        return route_event_model(
            originating_resource_name=self.resource_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            path=self.path,
            verb=self.verb,
            api_id=self.api_id.render(),
            route_id=self.route_id.render()
        )

########################
##### Output
########################
class ApiOutput(ResourceOutputs):
    """Container object for the returned values from the cloud after the resource has been deployed."""
    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)
    
    @property
    def endpoint(self) -> Cloud_Output_Str:
        """The base url for the created API

        Returns:
            Cloud_Output_Str: base url
        """
        return Cloud_Output_Str(
            name=self._name,
            ruuid=RUUID,
            key='endpoint',
            type=self.OUTPUT_TYPE
        )

    @endpoint.setter
    def endpoint(self, value: Any):
        raise Exception


    @property
    def endpoints(self) -> Cloud_Output_Mapping[Cloud_Output_Str]:
        """The created routes for the API.

        Values are stored as a mapping of the (path,verb) to cloud route_id.  
        
        ex:
            {
                '/hello_world [GET]': <route_id>
            }

        Returns:
            Cloud_Output_Mapping[Cloud_Output_Str]: Routes
        """
        return Cloud_Output_Mapping[Cloud_Output_Str](
            name=self._name,
            ruuid=RUUID,
            key='endpoints',
            type=self.OUTPUT_TYPE,
            _member_class=Cloud_Output_Str
        )

    @endpoints.setter
    def endpoints(self, value: Any):
        raise Exception


########################
##### Api
########################


class simple_api_model(ResourceModel):
    routes: FrozenSet[route_model]
    allow_cors: bool


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
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.

        Note:
            To create routes for the api use the `route` method
        """

        super().__init__(cdev_name, RUUID, nonce)
        
        self._allow_cors = allow_cors
        self._routes: List[Route] = []
        self.output = ApiOutput(cdev_name)

    @property
    def allow_cors(self):
        return self._allow_cors

    @allow_cors.setter
    @update_hash
    def allow_cors(self, value: bool):
        self._allow_cors = value

    @update_hash
    def route(self, path: str, verb: str) -> Route:
        """Create a route for the API.

        Generate a `RouteEvent` that can be used as a trigger for other resources. In particular, you can attach a serverless
        function to the route to handle the event.

        ```
        route = myApi.route('/hello_world')
        ```

        Args:
            path (str): The http path of the route created. Path must start with '/'.
            verb (str): Options: GET, PUT, POST, DELETE, ANY 

        Returns:
            RouteEvent: The event is created. 
        """
    
        event = Route(
            self.name,
            path, 
            verb
        )

        self._routes.append(event)

        return event

    def compute_hash(self):
        self._hash = hasher.hash_list(
            [
                hasher.hash_list([x.hash() for x in self._routes]),
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
