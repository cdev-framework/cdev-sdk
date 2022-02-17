"""Set of constructs for making Serverless Functions

"""

import importlib
import inspect
import os
from pydantic import FilePath
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Union

from core.constructs.cloud_output import Cloud_Output, Cloud_Output_Dynamic, Cloud_Output_Str
from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs, PermissionsGrantableMixin
from core.constructs.models import frozendict, ImmutableModel
from core.constructs.types import cdev_str_model, cdev_str

from core.utils import hasher
from core.utils.platforms import lambda_python_environment, get_current_closest_platform

from core.default.resources.simple.iam import Permission, PermissionArn, permission_arn_model, permission_model
from core.default.resources.simple.events import Event, event_model


LAMBDA_LAYER_RUUID = "cdev::simple::lambda_layer"
RUUID = "cdev::simple::function"

################
##### Dependencies 
################
class DeployedLayer():
    """Construct that represents a Layer already deployed on the Cloud"""
    def __init__(self, arn: str) -> None:
        self.arn = arn


class dependency_layer_model(ResourceModel):
    """Model that represents a local folder that will be deployed on the cloud as a Layer"""
    artifact_path: str


class DependencyLayer(Resource):
    """Construct that represents a local folder that will be deployed on the cloud as a Layer"""
    def __init__(self, cdev_name: str, artifact_path: FilePath, artifact_hash: str) -> None:
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
            artifact_path=self.artifact_path
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
            name=self._name,
            ruuid=LAMBDA_LAYER_RUUID,
            key='arn',
            type=self.OUTPUT_TYPE
        )

    @layer_arn.setter
    def layer_arn(self, value: Any):
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

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data 
        frozen = True


class SimpleFunctionConfiguration():
    """Container for the configuration settings of Serverless Function"""
    def __init__(self, handler: cdev_str, description: cdev_str = "", environment_variables: Dict[str, cdev_str] = {} ) -> None:
        """
        Args:
            handler (cdev_str): The python module path of the handler function that is triggered by the Cloud Platform
            description (cdev_str, optional): A description of the Function. Defaults to "".
            environment_variables (Dict[str, cdev_str], optional): A dict of overriding variabled for the Environment. Defaults to {}.
        """
        self.handler = handler
        self.description = description
        self.environment_variables = environment_variables


    def render(self) -> simple_function_configuration_model:
        return simple_function_configuration_model(
            handler=self.handler.render() if isinstance(self.handler, Cloud_Output_Dynamic) else self.handler,
            description=self.description.render() if isinstance(self.description, Cloud_Output_Dynamic) else self.description,
            environment_variables = frozendict(
                {k:frozendict(v.render().dict()) if isinstance(v, Cloud_Output) else v for k,v in self.environment_variables.items()}
            ) if self.environment_variables else frozendict({})
        )

    def hash(self) -> str:
        env_hashable = {k:(v if not isinstance(v, Cloud_Output) else v.hash()) for k,v in self.environment_variables.items()} 


        return hasher.hash_list([
            self.handler,
            self.description,
            hasher.hash_list(sorted(env_hashable.items()))
        ])



class simple_function_model(ResourceModel):
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



class SimpleFunction(PermissionsGrantableMixin, Resource):
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
        external_dependencies: List[Union[DeployedLayer, DependencyLayer]]=[],
        src_code_hash: str = None,
        nonce: str = "",
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
            nonce (str, optional): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
        """
        super().__init__(cdev_name, RUUID, nonce)

        self._filepath = filepath
        self._events = events
        self._configuration = configuration
        self._external_dependencies = external_dependencies
        self._granted_permissions: List[Union[Permission, PermissionArn]] = function_permissions

        self.src_code_hash = src_code_hash if src_code_hash else hasher.hash_file(filepath)

        self._platform = platform if platform else get_current_closest_platform()
        

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    @update_hash
    def filepath(self, value: str):
        self._filepath = value

    @property
    def events(self):
        return self._events

    @events.setter
    @update_hash
    def events(self, value: List[Event]):
        self._events = value

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    @update_hash
    def configuration(self, value: SimpleFunctionConfiguration):
        self._configuration = value

    @property
    def platform(self):
        return self._platform

    @platform.setter
    @update_hash
    def platform(self, value: lambda_python_environment):
        self._platform = value

    @property
    def external_dependencies(self):
        return self._external_dependencies

    @external_dependencies.setter
    @update_hash
    def external_dependencies(self, value: List[Union[DeployedLayer, DependencyLayer]]):
        self._external_dependencies = value

    def compute_hash(self):
        self._permissions_hash = hasher.hash_list([x.hash() for x in self._granted_permissions])
        self._config_hash = self._configuration.hash()
        self._events_hash = hasher.hash_list([x.hash() for x in self.events])

        self._hash = hasher.hash_list(
            [
                self.src_code_hash,
                self._config_hash,
                self._events_hash,
                self._permissions_hash,
                self._nonce,
                self._platform
            ]
        )

    def render(self) -> simple_function_model:

        premissions = [x.render() for x in self.granted_permissions]

        dependencies = [x.output.cloud_id.render() if isinstance(x, DependencyLayer) else x.arn for x in self.external_dependencies]
        
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
            platform=self.platform
        )


def simple_function_annotation(
    name: str,
    events: List[Event] = [],
    environment={},
    permissions: List[Union[Permission, PermissionArn]] = [],
    override_platform: lambda_python_environment = None,
    includes: List[str] = [],
    nonce: str=""
) -> Callable[[Callable], SimpleFunction]:
    """This annotation is used to designate that a function should be deployed as a Serverless function.

    Args:
        name (str): Cdev Name for the function
        events (List[Event], optional): List of event triggers for the function. Defaults to [].
        environment (dict, optional): Dictionary to apply to the Environment Variables of the deployed function. Defaults to {}.
        permissions (List[Union[Permission, PermissionArn]], optional): List of Permissions to grant to the Function. Defaults to [].
        override_platform (lambda_python_environment, optional): Option to override the deployment platform in the Cloud. Defaults to None.
        includes (List[str], optional): Set of identifiers to extra global statements to include in parsed artifacts. Defaults to [].
        nonce (str, optional): Nonce to make the resource hash unique if there are conflicting resources with same configuration.

    Returns:
        Callable[[Callable], SimpleFunction]: wrapper that returns the `SimpleFunction`
    """

    def create_function(func: Callable) -> SimpleFunction:

        if inspect.isfunction(func):
            for item in inspect.getmembers(func):

                if item[0] == "__name__":
                    handler_name = item[1]
                elif item[0] == "__doc__":
                    description = item[1] if item[1] else ""
                elif item[0] == "__module__":
                    mod_name = item[1]


        final_config = SimpleFunctionConfiguration(
            handler=handler_name,
            description=description,
            environment_variables=environment
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
            nonce=nonce
        )

    return create_function
