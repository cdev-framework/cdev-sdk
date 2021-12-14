from enum import Enum
from typing_extensions import Literal
from typing import Dict, List, Optional, Union

from pydantic.main import BaseModel
from pydantic import FilePath
from pydantic.types import DirectoryPath

from sortedcontainers.sorteddict import SortedDict

import importlib
import inspect
import os

from pathlib import PosixPath, WindowsPath

from core.constructs.resource import ResourceModel, Cloud_Output, Resource
from core.utils import hasher, logger
from cdev.utils import parent_resources, environment as cdev_environment

log = logger.get_cdev_logger(__name__)


LAMBDA_LAYER_RUUID = "cdev::simple::lambda_layer"
LAMBDA_FUNCTION_RUUID = "cdev::simple::lambda_function"


class simple_lambda_layer_output(str, Enum):
    arn = "arn"


class DependencyLayerModel(ResourceModel):
    artifact_path: Optional[FilePath]
    
    def __init__(__pydantic_self__, name: str, ruuid: str, artifact_path: FilePath=None) -> None:
        super().__init__(**{
            "name": name,
            "ruuid": ruuid,
            "artifact_path": artifact_path
        })

    





class DependencyLayer(Resource):
    RUUID = "cdev::simple::dependencylayer"
    
    def __init__(self, name: str, artifact_path: FilePath = None) -> None:
        super().__init__(name)
        self.artifact_path = artifact_path

    
    def from_output(self, key: simple_lambda_layer_output) -> Cloud_Output:
        return Cloud_Output(**{"resource": f"{self.RUUID}::{self.name}", "key": key.value, "type": "cdev_output"})


    def render(self) -> DependencyLayerModel:
        return DependencyLayerModel(
            self.name,
            self.RUUID,
            self.artifact_path
        )
    


class LambdaLayerArn(ResourceModel):
    arn: str




class EventTypes(Enum):
    HTTP_API_ENDPOINT = "api::endpoint"
    TABLE_STREAM = "table::stream"
    BUCKET_TRIGGER = "bucket:trigger"
    QUEUE_TRIGGER = "queue::trigger"
    TOPIC_TRIGGER = "topic::trigger"


class Event(BaseModel):
    original_resource_name: str

    original_resource_type: str

    event_type: EventTypes

    config: Dict


    def get_hash(self) -> str:
        return hasher.hash_list([self.original_resource_name, self.original_resource_type, SortedDict(self.config)])


class Permission(BaseModel):
    actions: List[str]
    resource: str
    effect: Union[Literal["Allow"], Literal["Deny"]]
    resource_suffix: Optional[str]
    
    def __init__(self, actions: List[str], resource: str, effect: Union[Literal["Allow"], Literal["Deny"]], resource_suffix: Optional[str]=""):
        """
        Create a permission object that can be attached to a lambda function to give it permission to access other resources.

        args:
            actions (List[str]): List of the IAM actions that this policy will include
            resource (str): The Cdev resource name that this policy is for. Note this is not the aws resource name. A lookup will occur to map the cdev name to aws resource
            effect ('Allow', 'Deny'): Allow or Deny the permission
            resource_suffix (Optional[str]): Some permissions need suffixes added to the looked up aws resource (i.e. dynamodb streams )
        """
        super().__init__(**{
            "actions": actions,
            "resource": resource,
            "effect": effect,
            "resource_suffix": resource_suffix
        })

    def get_hash(self) -> str:
        return hasher.hash_list([self.resource, hasher.hash_list(self.actions), self.effect, self.resource_suffix])



class PermissionArn(BaseModel):
    arn: str

    def get_hash(self) -> str:
        return hasher.hash_string(self.arn)



class lambda_function_configuration_environment(BaseModel):
    Variables: Dict[str, Union[str, Cloud_Output]]

    def __init__(__pydantic_self__, Variables: Dict[str, Union[str, Cloud_Output]]) -> None:
        super().__init__(**{
            "Variables": Variables
        })

    def get_cdev_hash(self):
        sorted_dic = SortedDict(self.Variables)
        
        as_list = [f"{k}:{v}" for (k,v) in sorted_dic.items() ]
        return hasher.hash_list(as_list)


class lambda_function_configuration(BaseModel):
    Handler: Union[str,None]
    Description: Union[str,None]
    Environment: Union[lambda_function_configuration_environment, None]


    def get_cdev_hash(self) -> str:
        if self.Environment:
            env_hash = self.Environment.get_cdev_hash()
        else: 
            env_hash = ""
        rv = hasher.hash_list([self.Description, env_hash, self.Handler])
        return rv


class simple_aws_lambda_function_model(ResourceModel):
    """
    An aws lambda function
    """

    function_name: str
    filepath: str # Don't use FilePath because this will be a relative path and might not always point correctly to a file in all contexts
    configuration: lambda_function_configuration
    events: List[Event]
    permissions: List[Union[Permission,PermissionArn]]
    src_code_hash: str
    external_dependencies_hash: Optional[str]
    external_dependencies: Optional[List[Union[LambdaLayerArn, DependencyLayer, Cloud_Output]]]
    config_hash: str
    events_hash: str
    permissions_hash: str

    class Config:
        json_encoders = {
            PosixPath: lambda v: v.as_posix(), # or lambda v: str(v)
            WindowsPath: lambda v: v.as_posix()
        }

        extra='ignore'


class simple_lambda(Resource):
    def __init__(self, cdev_name: str, filepath: str, function_name: str="" ,events: List[Event]=[], configuration: lambda_function_configuration={}, function_permissions: List[Union[Permission,PermissionArn]]=[] ,includes: List[str]=[]) -> None:
        super().__init__(cdev_name)

        self.filepath = filepath
        self.includes = includes
        self.events = events
        self.function_name = f"{function_name}_{cdev_environment.get_current_environment_hash()}" if function_name else f"{cdev_name}_{cdev_environment.get_current_environment_hash()}"

        self.configuration = configuration
        config_parents = [f"{'::'.join(x.resource.split('::')[:3])};hash;{x.resource.split('::')[-1]}" for x in parent_resources.find_cloud_output(configuration.dict())]
        
        
        self._permissions = function_permissions
        self.permissions_hash = hasher.hash_list([x.get_hash for x in function_permissions])
        permissions_parents = [f"{'::'.join(x.resource.split('::')[:-1])};name;{x.resource.split('::')[-1]}" for x in function_permissions if isinstance(x, Permission)]
        


        self.src_code_hash = hasher.hash_file(filepath)
        self.config_hash = configuration.get_cdev_hash()
        self.events_hash = hasher.hash_list([x.get_hash() for x in events])

        self.external_dependencies_hash = None
        self.external_dependencies = None

        self.full_hash = hasher.hash_list([self.function_name, self.src_code_hash, self.config_hash, self.events_hash, self.permissions_hash])

        event_parents = [f"{x.original_resource_type};name;{x.original_resource_name}" for x in events]
        all_parents = event_parents + config_parents + permissions_parents
        self.parents = all_parents
        log.info(f"ALL PARENTS {self.parents}")


    def render(self) -> simple_aws_lambda_function_model:
       
        return simple_aws_lambda_function_model(**{
            "name": self.name,
            "ruuid": LAMBDA_FUNCTION_RUUID,
            "hash": self.full_hash,
            "function_name": self.function_name,
            "filepath": self.filepath,
            "events": self.events,
            "permissions": self._permissions,
            "configuration": self.configuration,
            "permissions_hash": self.permissions_hash,
            "src_code_hash": self.src_code_hash,
            "config_hash": self.config_hash,
            "events_hash": self.events_hash,
            "parent_resources": self.parents,
            "external_dependencies_hash": self.external_dependencies_hash,
            "external_dependencies": self.external_dependencies
        })
        

    def get_includes(self) -> List[str]:
        return self.includes




def simple_lambda_function_annotation(name: str, function_name: str="", events: List[Event]=[],  Environment={}, Permissions: List[Union[Permission,PermissionArn]]=[], includes: List[str]=[]):
    """
    This annotation is used to designate that a function should be deployed on the AWS lambda platform. Functions that are designated
    using this annotation should have a signature that takes two inputs (event,context) to conform to the aws lambda handler signature.

    Functions that are annotated with this symbol will be put through the cdev function parser to optimize the final deployed artifact
    to only contain global statements needed for this function. For more information on this process read <link>.

    """

    def create_function(func) -> simple_lambda:
        
        log.info(func)
        if inspect.isfunction(func):
            for item in inspect.getmembers(func):
                
                if item[0] == "__name__":
                    handler_name=item[1]
                elif item[0] == "__doc__":
                    description = item[1] if item[1] else ""
                elif item[0] == "__module__":
                    mod_name = item[1]


        base_config = {
        
        }

        base_config["Environment"] = {"Variables": Environment} if Environment else None
        base_config["Description"] = description
        base_config["Handler"] = handler_name


        final_config = lambda_function_configuration(**base_config)

        mod = importlib.import_module(mod_name)

        full_filepath = os.path.abspath(mod.__file__)
        
        return simple_lambda(cdev_name=name, filepath=full_filepath, function_name=function_name ,events=events, configuration=final_config, function_permissions=Permissions ,includes=includes)

    
   
    return create_function
        





