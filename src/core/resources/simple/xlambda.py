from enum import Enum
import importlib
import inspect
import os
from pydantic import FilePath
from typing import Callable, FrozenSet, List, Optional, Union

from core.constructs.resource import Resource, ResourceModel, Cloud_Output, update_hash
from core.utils import hasher
from core.utils.types import frozendict, ImmutableModel

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

class layer_output(str, Enum):
    arn = "arn"

class DeployedLayer():
    pass


class dependency_layer_model(ResourceModel):
    artifact_path: str


class simple_lambda_layer_output(str, Enum):
    arn = "arn"


class DependencyLayer(Resource):
    RUUID = "cdev::simple::dependencylayer"

    def __init__(self, name: str, artifact_path: FilePath = None) -> None:
        super().__init__(name)
        self.artifact_path = artifact_path

    def from_output(self, key: layer_output) -> Cloud_Output:
        return super().from_output(key)


    def render(self) -> dependency_layer_model:
        return dependency_layer_model(
            ruuid=self.RUUID,
            name=self.name, 
            hash='1',
            artifact_path=self.artifact_path
        )


################
##### Function
################
class simple_function_configuration_model(ImmutableModel):
    handler: str
    description: Optional[str]
    environment_variables: frozendict

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data 
        frozen = True



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


class SimpleFunction(Resource):
    @update_hash
    def __init__(
        self,
        cdev_name: str,
        filepath: str,
        events: List[Event] = [],
        configuration: simple_function_configuration_model = {},
        function_permissions: List[Union[Permission, PermissionArn]] = [],
        external_dependencies: List[Union[DeployedLayer, DependencyLayer]]=[],
        src_code_hash: str = None,
        nonce: str = "",
    ) -> None:
        super().__init__(cdev_name, RUUID, nonce)

        self._filepath = filepath
        self._events = events
        self._configuration = configuration
        self._permissions = function_permissions
        self._external_dependencies = external_dependencies
        
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
    def configuration(self, value: simple_function_configuration_model):
        self._configuration = value

    @property
    def permissions(self):
        return self._permissions

    @permissions.setter
    @update_hash
    def permissions(self, value: List[Union[Permission, PermissionArn]]):
        self._permissions = value

    @property
    def external_dependencies(self):
        return self._external_dependencies

    @external_dependencies.setter
    @update_hash
    def external_dependencies(self, value: List[Union[DeployedLayer, DependencyLayer]]):
        self._external_dependencies = value

    def compute_hash(self):
        self._permissions_hash = "1"
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

        return simple_function_model(
            name=self.name,
            ruuid=self.ruuid,
            hash=self.hash,
            filepath=self.filepath,
            configuration=self.configuration,
            events=frozenset([x.render() for x in self.events]),
            permissions=frozenset([x.render() for x in self.permissions]),
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


        final_config = simple_function_configuration_model(
            handler=handler_name,
            description=description,
            environment_variables= frozendict(environment) if environment else frozendict({})
        )

        mod = importlib.import_module(mod_name)

        full_filepath = os.path.abspath(mod.__file__)

        return SimpleFunction(
            cdev_name=name,
            filepath=full_filepath,
            events=events,
            configuration=final_config,
            function_permissions=permissions,
            includes=includes,
            nonce=nonce
        )

    return create_function
