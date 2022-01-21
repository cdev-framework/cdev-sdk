from enum import Enum
import importlib
import inspect
import os
from pydantic import FilePath
from typing import Callable, FrozenSet, List, Optional, Union

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher
from core.utils.types import frozendict, ImmutableModel

from .iam import Permission, PermissionArn, permission_arn_model, permission_model
from .events import Event, event_model


LAMBDA_LAYER_RUUID = "cdev::simple::lambda_layer"
LAMBDA_FUNCTION_RUUID = "cdev::simple::function"

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
##### Functions
################
class simple_function_configuration_model(ImmutableModel):
    handler: str
    description: Optional[str]
    environment_variables: frozendict

    class Config:
        use_enum_values = True
        # Beta Feature but should be fine since this is simple data 
        frozen = True


class FunctionConfiguration():
    pass


class simple_function_model(ResourceModel):
    function_name: str
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
    def __init__(
        self,
        cdev_name: str,
        filepath: str,
        function_name: str = "",
        events: List[Event] = [],
        configuration: FunctionConfiguration = {},
        function_permissions: List[Union[Permission, PermissionArn]] = [],
        includes: List[str] = [],
        external_dependencies: List[Union[DeployedLayer, DependencyLayer]]=[],
        src_code_hash: str = None
    ) -> None:
        super().__init__(cdev_name)

        self.filepath = filepath
        self.includes = includes
        self.events = events
        self.function_name = (
            function_name
            if function_name
            else "cdev_serverless_function"
        )

        self.configuration = configuration


        self._permissions = function_permissions
        
        self.permissions_hash = "1"

        self.src_code_hash = src_code_hash if src_code_hash else hasher.hash_file(filepath)

        self.config_hash = "1"

        self.events_hash = hasher.hash_list([x.get_hash() for x in events])

        self.external_dependencies = external_dependencies

        self.full_hash = hasher.hash_list(
            [
                self.function_name,
                self.src_code_hash,
                self.config_hash,
                self.events_hash,
                self.permissions_hash,
            ]
        )

        
    def render(self) -> simple_function_model:

        return simple_function_model(
            name=self.name,
            ruuid=LAMBDA_FUNCTION_RUUID,
            hash=self.full_hash,
            function_name=self.function_name,
            filepath=self.filepath,
            configuration=self.configuration,
            events=frozenset([x.render() for x in self.events]),
            permissions=frozenset([x.render() for x in self._permissions]),
            external_dependencies=self.external_dependencies,
            src_code_hash=self.src_code_hash
        )

    def get_includes(self) -> List[str]:
        return self.includes




def simple_function_annotation(
    name: str,
    function_name: str = "",
    events: List[Event] = [],
    environment={},
    permissions: List[Union[Permission, PermissionArn]] = [],
    includes: List[str] = [],
) -> Callable[[Callable], SimpleFunction]:
    """
    This annotation is used to designate that a function should be deployed on the AWS lambda platform. Functions that are designated
    using this annotation should have a signature that takes two inputs (event,context) to conform to the aws lambda handler signature.

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
            function_name=function_name,
            events=events,
            configuration=final_config,
            function_permissions=permissions,
            includes=includes,
        )

    return create_function
