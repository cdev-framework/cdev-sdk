"""Set of constructs for making Serverless Functions

"""

import importlib
import inspect
import os

from core.default.resources.simple.api import RouteEvent
from pydantic import FilePath
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Union

from core.constructs.cloud_output import (
    Cloud_Output,
    Cloud_Output_Dynamic,
    Cloud_Output_Str,
)
from core.constructs.resource import (
    Resource,
    TaggableResourceModel,
    TaggableMixin,
    update_hash,
    ResourceOutputs,
    PermissionsGrantableMixin,
)
from core.constructs.models import frozendict, ImmutableModel
from core.constructs.types import cdev_str_model, cdev_str, cdev_int

from core.utils import hasher
from core.utils.platforms import lambda_python_environment, get_current_closest_platform

from core.default.resources.simple.iam import (
    Permission,
    PermissionArn,
    permission_arn_model,
    permission_model,
)
from core.default.resources.simple.events import Event, event_model


LAMBDA_LAYER_RUUID = "cdev::simple::lambda_layer"
RUUID = "cdev::simple::function"

###################
##### Exceptions
###################
class CallableError(Exception):
    pass


################
##### Dependencies
################
class DeployedLayer:
    """Construct that represents a Layer already deployed on the Cloud"""

    def __init__(self, arn: str) -> None:
        self.arn = arn


class dependency_layer_model(TaggableResourceModel):
    """Model that represents a local folder that will be deployed on the cloud as a Layer"""

    artifact_path: str


class DependencyLayer(Resource):
    """Construct that represents a local folder that will be deployed on the cloud as a Layer"""

    def __init__(
        self, cdev_name: str, artifact_path: FilePath, artifact_hash: str
    ) -> None:
        super().__init__(cdev_name, LAMBDA_LAYER_RUUID)
        self.artifact_path = artifact_path
        self.artifact_hash = artifact_hash
        self._hash = artifact_hash
        self.output = DependencyLayerOutput(cdev_name)

    def render(self) -> dependency_layer_model:
        return dependency_layer_model(
            ruuid=LAMBDA_LAYER_RUUID,
            name=self.name,
            hash=self.artifact_hash,
            tags=frozendict({}),
            artifact_path=self.artifact_path,
        )


################
##### Output
################


class DependencyLayerOutput(ResourceOutputs):
    """Container object for the returned values from the cloud after a Layer has been deployed."""

    def __init__(self, name: str) -> None:
        super().__init__(name, LAMBDA_LAYER_RUUID)

    @property
    def layer_arn(self) -> Cloud_Output_Str:
        """The id of the created layer"""
        return Cloud_Output_Str(
            name=self._name, ruuid=LAMBDA_LAYER_RUUID, key="arn", type=self.OUTPUT_TYPE
        )

    @layer_arn.setter
    def layer_arn(self, value: Any) -> None:
        raise Exception


class FunctionOutput(ResourceOutputs):
    """Container object for the returned values from the cloud after a Serverless Function has been deployed."""

    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)


################
##### Function
################
class simple_function_configuration_model(ImmutableModel):
    """Model representing the configuration of a Serverless Function"""

    handler: str
    description: Optional[cdev_str_model]
    environment_variables: frozendict
    memory_size: int
    timeout: int
    storage: int

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data
        frozen = True


class SimpleFunctionConfiguration:
    """Container for the configuration settings of Serverless Function"""

    def __init__(
        self,
        handler: cdev_str,
        memory_size: cdev_int,
        timeout: cdev_int,
        storage: cdev_int,
        description: cdev_str = "",
        environment_variables: Dict[str, cdev_str] = {},
    ) -> None:
        """
        Args:
            handler (cdev_str): The python module path of the handler function that is triggered by the Cloud Platform
            description (cdev_str, optional): A description of the Function. Defaults to "".
            environment_variables (Dict[str, cdev_str], optional): A dict of overriding variabled for the Environment. Defaults to {}.
        """
        self.handler = handler
        self.memory_size = memory_size
        self.timeout = timeout
        self.storage = storage
        self.description = description
        self.environment_variables = environment_variables

    def render(self) -> simple_function_configuration_model:
        return simple_function_configuration_model(
            handler=self.handler.render()
            if isinstance(self.handler, Cloud_Output_Dynamic)
            else self.handler,
            memory_size=self.memory_size.render()
            if isinstance(self.memory_size, Cloud_Output_Dynamic)
            else self.memory_size,
            timeout=self.timeout.render()
            if isinstance(self.timeout, Cloud_Output_Dynamic)
            else self.timeout,
            storage=self.storage.render()
            if isinstance(self.storage, Cloud_Output_Dynamic)
            else self.storage,
            description=self.description.render()
            if isinstance(self.description, Cloud_Output_Dynamic)
            else self.description,
            environment_variables=frozendict(
                {
                    k: frozendict(v.render().dict())
                    if isinstance(v, Cloud_Output)
                    else v
                    for k, v in self.environment_variables.items()
                }
            )
            if self.environment_variables
            else frozendict({}),
        )

    def hash(self) -> str:
        env_hashable = {
            k: (v if not isinstance(v, Cloud_Output) else v.hash())
            for k, v in self.environment_variables.items()
        }

        return hasher.hash_list(
            [
                self.handler,
                self.memory_size,
                self.timeout,
                self.storage,
                self.description,
                hasher.hash_list(sorted(env_hashable.items())),
            ]
        )


class simple_function_model(TaggableResourceModel):
    """Model representing a Serverless Function

    Args:
        Filepath ([type]): [description]
    """

    filepath: str  # Don't use FilePath because this will be a relative path and might not always point correctly to a file in all contexts
    configuration: simple_function_configuration_model
    events: FrozenSet[event_model]
    permissions: FrozenSet[Union[permission_model, permission_arn_model]]
    external_dependencies: FrozenSet[Any]
    src_code_hash: str
    platform: lambda_python_environment


class SimpleFunction(PermissionsGrantableMixin, TaggableMixin, Resource):
    """Construct to represent a Serverless Function. It is recommend to generate this resource using the `simple_function_annotation`"""

    @update_hash
    def __init__(
        self,
        cdev_name: str,
        filepath: str,
        configuration: SimpleFunctionConfiguration,
        events: List[Event] = [],
        platform: lambda_python_environment = None,
        function_permissions: List[Union[Permission, PermissionArn]] = [],
        external_dependencies: List[Union[DeployedLayer, DependencyLayer]] = [],
        src_code_hash: str = None,
        preserve_function: Callable = None,
        nonce: str = "",
        tags: Dict[str, str] = {},
    ) -> None:
        """

        Args:
            cdev_name (str): Cdev Name for the function
            filepath (str): Path the final artifact to upload.
            configuration (SimpleFunctionConfiguration):  Configuration options for the function.
            events (List[Event], optional):  List of event triggers for the function.. Defaults to [].
            platform (lambda_python_environment, optional): Option to override the deployment platform in the Cloud.. Defaults to None.
            function_permissions (List[Union[Permission, PermissionArn]], optional): List of Permissions to grant to the Function.. Defaults to [].
            external_dependencies (List[Union[DeployedLayer, DependencyLayer]], optional): Dependencies to link to in the Cloud. Defaults to [].
            src_code_hash (str, optional): identifying hash of the source code. Defaults to None.
            preserve_function (Callable, optional): the original function that is being deployed. This allows the returned object ro remain Callable. Default to None.
            nonce (str, optional): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
            tags (Dict[str, str]): A set of tags to add to the resource
        """

        super().__init__(name=cdev_name, ruuid=RUUID, nonce=nonce, tags=tags)

        self._filepath = filepath
        self._events = events
        self._configuration = configuration
        self._external_dependencies = external_dependencies
        self._granted_permissions: List[
            Union[Permission, PermissionArn]
        ] = function_permissions

        self.src_code_hash = (
            src_code_hash if src_code_hash else hasher.hash_file(filepath)
        )

        self._platform = platform or get_current_closest_platform()

        self._preserved_function = preserve_function
        self.__annotations__ = preserve_function.__annotations__
        self.__doc__ = preserve_function.__doc__

    @property
    def filepath(self) -> str:
        return self._filepath

    @filepath.setter
    @update_hash
    def filepath(self, value: str) -> None:
        self._filepath = value

    @property
    def events(self) -> List[Event]:
        return self._events

    @events.setter
    @update_hash
    def events(self, value: List[Event]) -> None:
        self._events = value

    @property
    def configuration(self) -> SimpleFunctionConfiguration:
        return self._configuration

    @configuration.setter
    @update_hash
    def configuration(self, value: SimpleFunctionConfiguration):
        self._configuration = value

    @property
    def platform(self) -> lambda_python_environment:
        return self._platform

    @platform.setter
    @update_hash
    def platform(self, value: lambda_python_environment) -> None:
        self._platform = value

    @property
    def external_dependencies(self) -> List[Union[DeployedLayer, DependencyLayer]]:
        return self._external_dependencies

    @external_dependencies.setter
    @update_hash
    def external_dependencies(
        self, value: List[Union[DeployedLayer, DependencyLayer]]
    ) -> None:
        self._external_dependencies = value

    def compute_hash(self) -> None:
        permissions_hash = hasher.hash_list(
            [x.hash() for x in self._granted_permissions]
        )

        self._hash = hasher.hash_list(
            [
                self.src_code_hash,
                self._configuration.hash(),
                hasher.hash_list([x.hash() for x in self.events]),
                permissions_hash,
                self._nonce,
                self._platform,
                self._get_tags_hash(),
            ]
        )

    def render(self) -> simple_function_model:

        premissions = [x.render() for x in self.granted_permissions]

        dependencies = [
            x.output.cloud_id.render() if isinstance(x, DependencyLayer) else x.arn
            for x in self.external_dependencies
        ]

        return simple_function_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            configuration=self.configuration.render(),
            filepath=self.filepath,
            events=frozenset([x.render() for x in self.events]),
            permissions=frozenset(premissions),
            external_dependencies=frozenset(dependencies),
            src_code_hash=self.src_code_hash,
            platform=self.platform,
            tags=frozendict(self.tags),
        )

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if not self._preserved_function:
            raise CallableError

        return self._preserved_function(*args, **kwds)


def simple_function_annotation(
    name: str,
    events: List[Union[Event, RouteEvent]] = [],
    environment={},
    memory_size: int = 128,
    timeout: int = 30,
    storage: int = 512,
    permissions: List[Union[Permission, PermissionArn]] = [],
    override_platform: lambda_python_environment = None,
    includes: List[str] = [],
    nonce: str = "",
    tags: Dict[str, str] = None,
) -> Callable[[Callable], SimpleFunction]:
    """This annotation is used to designate that a function should be deployed as a Serverless function.

    Args:
        name (str): Cdev Name for the function
        events (List[Event], optional): List of event triggers for the function. Defaults to [].
        environment (dict, optional): Dictionary to apply to the Environment Variables of the deployed function. Defaults to {}.
        memory_size (int, optional): Memory Size of you lambda in MB. Default is 128.
        timeout (int, optional): Timeout of your lambda in seconds. Default is 30 sec and up to 900.
        storage (int, optional): Storage of your lambda in MB. Default is 512 MB and can be up to 10240.
        permissions (List[Union[Permission, PermissionArn]], optional): List of Permissions to grant to the Function. Defaults to [].
        override_platform (lambda_python_environment, optional): Option to override the deployment platform in the Cloud. Defaults to None.
        includes (List[str], optional): Set of identifiers to extra global statements to include in parsed artifacts. Defaults to [].
        nonce (str, optional): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
        tags (dict[str, str]): A set pf tags to use to identify the resource.

    Returns:
        Callable[[Callable], SimpleFunction]: wrapper that returns the `SimpleFunction`
    """

    def create_function(func: Callable) -> SimpleFunction:

        # ANIBAL are these optional???
        # confirm with Daniel
        handler_name = None
        description = None
        mod_name = None
        if inspect.isfunction(func):
            for item in inspect.getmembers(func):

                if item[0] == "__name__":
                    handler_name = item[1]
                elif item[0] == "__doc__":
                    description = item[1] or ""
                elif item[0] == "__module__":
                    mod_name = item[1]
        final_config = SimpleFunctionConfiguration(
            handler=handler_name,
            memory_size=memory_size,
            timeout=timeout,
            storage=storage,
            description=description,
            environment_variables=environment,
        )
        mod = importlib.import_module(mod_name)

        full_filepath = os.path.abspath(mod.__file__)

        return SimpleFunction(
            cdev_name=name,
            filepath=full_filepath,
            events=events,
            configuration=final_config,
            platform=override_platform,
            function_permissions=permissions,
            preserve_function=func,
            nonce=nonce,
            tags=tags,
        )

    return create_function
