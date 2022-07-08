"""Set of constructs for creating HTTP APIs

"""
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional, Union

from core.constructs.models import ImmutableModel, frozendict
from core.constructs.cloud_output import (
    Cloud_Output_Mapping,
    Cloud_Output_Str,
    OutputType,
)

from core.constructs.resource import (
    update_hash,
    Resource,
    ResourceOutputs,
    TaggableResourceModel,
    TaggableMixin,
)
from core.constructs.types import cdev_str_model
from core.utils import hasher

from core.default.resources.simple import events


RUUID = "cdev::simple::api"

########################
##### Authorizer
########################


class authorizer_model(ImmutableModel):
    """Model representing JWT authorizer information"""

    name: str
    issuer_url: str
    audience: str


class Authorizer:
    def __init__(self, name: str, issuer_url: str, audience: str) -> None:
        """JWT authorizer information.

        Deployed Apis can validates the JWTs that clients submit with API requests to allow or deny
        requests based on token validation, and optionally, scopes in the token. You can provide authorization
        from OpenID Connect (OIDC) and OAuth 2.0 frameworks.

        For examples on how to integrate with service like Auth0 visit our
        <a href="/docs/examples/user-authentication"> documentation </a>.


        Args:
            name (str): Name of the authorizer. Used as a unique identifier within the attached Api.
            issuer_url (str): The base domain of the identity provider that issues JSON Web Tokens.
            audience (str): The intended recipients of the JWT. A valid JWT must provide an aud that matches at this value.
        """
        self.name = name
        self.issuer_url = issuer_url
        self.audience = audience

    def render(self) -> authorizer_model:
        return authorizer_model(
            name=self.name,
            issuer_url=self.issuer_url,
            audience=self.audience,
        )

    def hash(self) -> str:
        return hasher.hash_list([self.name, self.issuer_url, self.audience])


########################
##### Route
########################
class route_verb(str, Enum):
    """Route Verbs"""

    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"
    ANY = "ANY"


class route_model(ImmutableModel):
    """Model to represent a route of an API"""

    path: str
    verb: str
    additional_scopes: Optional[FrozenSet[str]]
    authorizer_name: Optional[str]

    def __init__(__pydantic_self__, **data: Any) -> None:
        """"""
        super().__init__(**data)


class Route:
    def __init__(
        self,
        api_name: str,
        path: str,
        verb: route_verb,
        authorizer_name: str = None,
        additional_scopes: List[str] = [],
    ) -> None:
        """Construct for representing a route that is apart of an HTTP API

        Args:
            api_name (str): Cdev name of the API this route is apart of
            path (str): Path of the route.
            verb (route_verb): Verb that this route handles
            authorizer_name (str): The `name` of the authorizer to use for this route.
            additional_scopes (List[str]): Set of scopes that must be present in an authorization JWT.
        """
        self.api_name = api_name
        self.path = path
        self.verb = verb
        self.authorizer_name = authorizer_name
        self.additional_scopes = additional_scopes

    def hash(self) -> str:
        return hasher.hash_list(
            [
                self.path,
                self.verb,
                hasher.hash_list(self.additional_scopes),
                self.authorizer_name,
            ]
        )

    def render(self) -> route_model:
        return route_model(
            path=self.path,
            verb=self.verb,
            additional_scopes=frozenset(self.additional_scopes),
            authorizer_name=self.authorizer_name,
        )

    def event(self, response_type: Optional[str] = "") -> "RouteEvent":
        """Generate an Event Construct that other resources can bind to.

        Returns:
            `RouteEvent`
        """
        return RouteEvent(
            resource_name=self.api_name,
            path=self.path,
            verb=self.verb,
            response_type=response_type,
        )


class route_event_model(events.event_model):
    """Model to represent an event for a given route"""

    path: str
    verb: route_verb
    api_id: cdev_str_model
    route_id: cdev_str_model
    response_type: Optional[str]

    def __init__(__pydantic_self__, **data: Any) -> None:
        """"""
        super().__init__(**data)


class RouteEvent:
    """Construct for representing a route that is apart of an HTTP API."""

    def __init__(
        self,
        resource_name: str,
        path: str,
        verb: route_verb,
        response_type: Optional[str] = "",
    ) -> None:
        """
        Args:
            resource_name (str): Cdev Name of the API this event is generated from
            path (str): Path of the route
            verb (`route_verb`): Verb of the route

        This construct should be generated with the `Route.event` method.
        """
        self.resource_name = resource_name
        self.path = path
        self.verb = verb
        self.api_id = Cloud_Output_Str(
            name=resource_name, ruuid=RUUID, key="cloud_id", type=OutputType.RESOURCE
        )
        self.route_id = Cloud_Output_Mapping[Cloud_Output_Str](
            name=resource_name,
            ruuid=RUUID,
            key="endpoints",
            type=OutputType.RESOURCE,
            _member_class=Cloud_Output_Str,
        )[f"{self.path} {self.verb}"]

        self.response_type = response_type

    def hash(self) -> str:
        return hasher.hash_list(
            [self.resource_name, self.path, self.verb, self.response_type]
        )

    def render(self) -> route_event_model:
        return route_event_model(
            originating_resource_name=self.resource_name,
            originating_resource_type=RUUID,
            hash=self.hash(),
            path=self.path,
            verb=self.verb,
            api_id=self.api_id.render(),
            route_id=self.route_id.render(),
            response_type=self.response_type,
        )


########################
##### Output
########################
class ApiOutput(ResourceOutputs):
    """Container object for the returned values from the cloud after an API has been deployed."""

    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)

    @property
    def endpoint(self) -> Cloud_Output_Str:
        """The base url for the created API

        Returns:
            `core.constructs.cloud_output.Cloud_Output_Str`
        """
        return Cloud_Output_Str(
            name=self._name, ruuid=RUUID, key="endpoint", type=self.OUTPUT_TYPE
        )

    @endpoint.setter
    def endpoint(self, value: Any) -> None:
        raise Exception

    @property
    def endpoints(self) -> Cloud_Output_Mapping[Cloud_Output_Str]:
        """The created routes for the API.

        Values are stored as a mapping of the (path,verb) to cloud route_id.

        ex:
        ```
            {
                '/hello_world [GET]': <route_id>
            }
        ```

        Returns:
            `core.constructs.cloud_output.Cloud_Output_Mapping`
        """
        return Cloud_Output_Mapping[Cloud_Output_Str](
            name=self._name,
            ruuid=RUUID,
            key="endpoints",
            type=self.OUTPUT_TYPE,
            _member_class=Cloud_Output_Str,
        )

    @endpoints.setter
    def endpoints(self, value: Any) -> None:
        raise Exception


########################
##### Api
########################
class simple_api_model(TaggableResourceModel):
    """Model for representing a desired HTTP API"""

    routes: FrozenSet[route_model]
    allow_cors: bool
    authorizers: Optional[FrozenSet[authorizer_model]]

    def __init__(self, **data: Any) -> None:
        """"""
        super().__init__(**data)


class Api(TaggableMixin, Resource):
    @update_hash
    def __init__(
        self,
        cdev_name: str,
        allow_cors: bool = True,
        authorizers: List[Authorizer] = [],
        default_authorizer: str = None,
        nonce: str = "",
        tags: Dict[str, str] = None,
    ):
        """Create a HTTP API.

        Args:
            cdev_name (str): Name for the resource.
            allow_cors (bool): Allow Cross Origin Resource Sharing (CORS) on the api.
            authorizers (List[Authorizer]): List of JWT Authorizers for the api.
            default_authorizer (str): The name of an authorizer to add as the default to all routes.
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
            tags (Dict[str, str]): A set of tags to add to the resource

        With an HTTP API, you can create different routes that represent different requests to your backend service. Use the
        `route` method to create these routes then attach them to other resource to handle the requests.

        HTTP Api's can take an authorizer to support JWT authorization for the Api. You can provide a default authorizer to the Api to apply
        to all created routes, or individually set the authorizer for each route.

        <a href="https://code.tutsplus.com/tutorials/a-beginners-guide-to-http-and-rest--net-16340"> More information on HTTP routes</a>

        <a href="/docs/examples/api"> Examples on how to use in Cdev Framework </a>

        <a href="https://docs.aws.amazon.com/apigatewayv2/latest/api-reference/api-reference.html"> Documentation on Deployed Resource in the Cloud</a>

        <a href="https://aws.amazon.com/api-gateway/pricing/"> Details on pricing</a>
        """

        super().__init__(cdev_name, RUUID, nonce, tags=tags)

        self._allow_cors = allow_cors
        self._routes: List[Route] = []

        self._authorizers: List[Authorizer] = authorizers

        self._default_authorizer_name = default_authorizer

        self._output = ApiOutput(cdev_name)

    @property
    def output(self) -> ApiOutput:
        """Output generated by the Cloud when this resource is deployed."""
        return self._output

    @property
    def allow_cors(self) -> bool:
        """Allow the API to be accessed from sites other than the generated url.

        [Notes on CORS]
        """
        return self._allow_cors

    @allow_cors.setter
    @update_hash
    def allow_cors(self, value: bool) -> None:
        self._allow_cors = value

    @update_hash
    def route(
        self,
        path: str,
        verb: Union[route_verb, str],
        additional_scopes: List[str] = [],
        override_authorizer_name: str = None,
    ) -> Route:
        """Create a route for the API.

        Args:
            path (str): The http path of the route created
            verb (`route_verb`): verb for the path
            override_authorizer_name (str): The authorizer for this route. Overriding the default authorizer for the Api.
        Returns:
            `Route`

        Generate a `Route` that can be used as a trigger for other resources.

        ```
        route = myApi.route('/hello_world', 'GET')
        ```
        """

        authorizer_name = (
            override_authorizer_name
            if override_authorizer_name
            else self._default_authorizer_name
        )

        route = Route(self.name, path, verb, authorizer_name, additional_scopes)

        self._routes.append(route)

        return route

    def compute_hash(self) -> None:
        self._hash = hasher.hash_list(
            [
                hasher.hash_list([x.hash() for x in self._routes]),
                self.allow_cors,
                self.nonce,
                self._default_authorizer_name,
                self._get_tags_hash(),
                hasher.hash_list([x.hash() for x in self._authorizers]),
            ]
        )

    def render(self) -> simple_api_model:
        routes = frozenset(self._routes)

        return simple_api_model(
            ruuid=self.ruuid,
            name=self.name,
            hash=self.hash,
            routes=frozenset([x.render() for x in routes]),
            allow_cors=self.allow_cors,
            authorizers=frozenset([x.render() for x in self._authorizers]),
            tags=frozendict(self.tags)
        )
