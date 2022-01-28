from enum import Enum
import importlib
import inspect
import os
from pydantic import FilePath
from typing import Callable, Dict, FrozenSet, List, Optional, Union

from core.constructs.output import Cloud_Output_Dynamic
from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs, PermissionsGrantableMixin
from core.constructs.models import frozendict, ImmutableModel
from core.constructs.types import cdev_str_model, cdev_str

from core.utils import hasher

from .iam import Permission, PermissionArn, permission_arn_model, permission_model
from .events import Event, event_model


LAMBDA_LAYER_RUUID = "cdev::simple::lambda_layer"
RUUID = "cdev::simple::function"

################
##### Dependencies 
################
class deployed_layer_model(ResourceModel):
    arn: str
    version: str


class DeployedLayer():
    pass


class dependency_layer_model(ResourceModel):
    artifact_path: str


class DependencyLayer(Resource):

    def __init__(self, cdev_name: str, artifact_path: FilePath = None) -> None:
        super().__init__(cdev_name)
        self.artifact_path = artifact_path
        self.output = DependencyLayerOutput(cdev_name)

    def render(self) -> dependency_layer_model:
        return dependency_layer_model(
            ruuid=LAMBDA_LAYER_RUUID,
            name=self.name, 
            hash='1',
            artifact_path=self.artifact_path
        )

################
##### Output
################


class DependencyLayerOutput(ResourceOutputs):
    def __init__(self, name: str) -> None:
        super().__init__(name, LAMBDA_LAYER_RUUID)


class FunctionOutput(ResourceOutputs):
    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)


################
##### Function
################
class simple_function_configuration_model(ImmutableModel):
    handler: str
    description: Optional[cdev_str_model]
    environment_variables: frozendict

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data 
        frozen = True


class SimpleFunctionConfiguration():
    def __init__(self, handler: cdev_str, description: cdev_str = "", environment_variables: Dict[str, cdev_str] = {} ) -> None:
        self.handler = handler
        self.description = description
        self.environment_variables = environment_variables


    def render(self) -> simple_function_configuration_model:
        return simple_function_configuration_model(
            handler=self.handler.render() if isinstance(self.handler, Cloud_Output_Dynamic) else self.handler,
            description=self.description.render() if isinstance(self.description, Cloud_Output_Dynamic) else self.description,
            environment_variables = frozendict(
                {k:v.render() if isinstance(v, Cloud_Output_Dynamic) else v for k,v in self.environment_variables}
            ) if self.environment_variables else frozendict({})
        )



class simple_function_model(ResourceModel):
    """
    Some Doc String

    Args:
        Filepath ([type]): [description]
    """
    filepath: str  # Don't use FilePath because this will be a relative path and might not always point correctly to a file in all contexts
    configuration: simple_function_configuration_model
    events: FrozenSet[event_model]
    permissions: FrozenSet[Union[permission_model, permission_arn_model]]
    external_dependencies: FrozenSet[Union[deployed_layer_model, dependency_layer_model]]
    src_code_hash: str


    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data 
        frozen = True
        extra = "ignore"


class SimpleFunction(PermissionsGrantableMixin, Resource):
    @update_hash
    def __init__(
        self,
        cdev_name: str,
        filepath: str,
        configuration: SimpleFunctionConfiguration,
        events: List[Event] = [],
        function_permissions: List[Union[Permission, PermissionArn]] = [],
        external_dependencies: List[Union[DeployedLayer, DependencyLayer]]=[],
        src_code_hash: str = None,
        nonce: str = "",
    ) -> None:
        """[summary]

        Args:
            cdev_name (str): [description]
            filepath (str): [description]
            configuration (SimpleFunctionConfiguration): [description]. 
            events (List[Event], optional): [description]. Defaults to [].
            function_permissions (List[Union[Permission, PermissionArn]], optional): [description]. Defaults to [].
            external_dependencies (List[Union[DeployedLayer, DependencyLayer]], optional): [description]. Defaults to [].
            src_code_hash (str, optional): [description]. Defaults to None.
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
        """
        super().__init__(cdev_name, RUUID, nonce)

        self._filepath = filepath
        self._events = events
        self._configuration = configuration
        self._external_dependencies = external_dependencies
        self._granted_permissions: List[Union[Permission, PermissionArn]] = function_permissions

        self.src_code_hash = src_code_hash if src_code_hash else hasher.hash_file(filepath)
        

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
    def external_dependencies(self):
        return self._external_dependencies

    @external_dependencies.setter
    @update_hash
    def external_dependencies(self, value: List[Union[DeployedLayer, DependencyLayer]]):
        self._external_dependencies = value

    def compute_hash(self):
        self._permissions_hash = hasher.hash_list([x.hash() for x in self.granted_permissions])

        print(self._permissions_hash)
        self._config_hash = "1"
        self._events_hash = "1"

        self._hash = hasher.hash_list(
            [
                self.src_code_hash,
                self._config_hash,
                self._events_hash,
                self._permissions_hash,
                self._nonce
            ]
        )

    def render(self) -> simple_function_model:

        premissions = [x.render() for x in self.granted_permissions]
        
        return simple_function_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            configuration=self.configuration.render(),
            filepath=self.filepath,
            events=frozenset([x.render() for x in self.events]),
            permissions=frozenset(premissions),
            external_dependencies=self.external_dependencies,
            src_code_hash=self.src_code_hash
        )


def simple_function_annotation(
    name: str,
    events: List[Event] = [],
    environment={},
    permissions: List[Union[Permission, PermissionArn]] = [],
    includes: List[str] = [],
    nonce: str=""
) -> Callable[[Callable], SimpleFunction]:
    """This annotation is used to designate that a function should be deployed as a Serverless function. 
    
    Functions that are designated using this annotation should have a signature that takes two inputs (event,context) 
    to conform to the aws lambda handler signature.

    Functions that are annotated with this symbol will be put through the cdev function parser to optimize the final deployed artifact
    to only contain global statements needed for this function. For more information on this process read <link>.

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
            function_permissions=permissions,
            nonce=nonce
        )

    return create_function
