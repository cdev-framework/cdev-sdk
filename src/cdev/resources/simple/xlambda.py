from enum import Enum
from typing_extensions import Literal
from cdev.constructs import Cdev_Resource
from typing import Dict, List, Optional, Union

from pydantic.main import BaseModel
from pydantic import FilePath
from ...models import Rendered_Resource, Cloud_Output

from sortedcontainers.sorteddict import SortedDict

import importlib
import inspect
import os

from pathlib import PosixPath, WindowsPath
from cdev.utils import hasher, logger, parent_resources

log = logger.get_cdev_logger(__name__)

class EventTypes(Enum):
    HTTP_API_ENDPOINT = "api::endpoint"
    TABLE_STREAM = "table::stream"
    BUCKET_TRIGGER = "bucket:trigger"
    QUEUE_TRIGGER = "queue::trigger"


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
    
    def __init__(self, actions: List[str], resource: str, effect: Union[Literal["Allow"], Literal["Deny"]]):
        """
        Create a permission object that can be attached to a lambda function to give it permission to access other resources. 
        """
        super().__init__(**{
            "actions": actions,
            "resource": resource,
            "effect": effect
        })

    def get_hash(self) -> str:
        return hasher.hash_list([self.resource, hasher.hash_list(self.actions), self.effect])


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


class simple_aws_lambda_function_model(Rendered_Resource):
    """
    An aws lambda function
    """


    filepath: str # Don't use FilePath because this will be a relative path and might not always point correctly to a file in all contexts
    configuration: lambda_function_configuration
    events: List[Event]
    permissions: List[Union[Permission,PermissionArn]]
    src_code_hash: str
    config_hash: str
    events_hash: str
    permissions_hash: str

    class Config:
        json_encoders = {
            PosixPath: lambda v: v.as_posix(), # or lambda v: str(v)
            WindowsPath: lambda v: v.as_posix()
        }

        extra='ignore'


class simple_lambda(Cdev_Resource):
    def __init__(self, cdev_name: str, filepath: str,  events: List[Event]=[], configuration: lambda_function_configuration={}, permissions: List[Union[Permission,PermissionArn]]=[] ,includes: List[str]=[]) -> None:
        super().__init__(cdev_name)

        self.filepath = filepath
        self.includes = includes
        self.events = events

        self.configuration = configuration
        config_parents = [f"{'::'.join(x.resource.split('::')[:3])};hash;{x.resource.split('::')[-1]}" for x in parent_resources.find_cloud_output(configuration.dict())]
        
        self.permissions = permissions
        self.permissions_hash = hasher.hash_list([x.get_hash for x in permissions])
        permissions_parents = [f"{'::'.join(x.resource.split('::')[:-1])};name;{x.resource.split('::')[-1]}" for x in permissions if isinstance(x, Permission)]
        self.permissions.append(PermissionArn(**{
            "arn": "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        }))

        self.src_code_hash = hasher.hash_file(filepath)
        self.config_hash = configuration.get_cdev_hash()
        self.events_hash = hasher.hash_list([x.get_hash() for x in events])

        self.full_hash = hasher.hash_list([self.src_code_hash, self.config_hash, self.events_hash, self.permissions_hash])

        event_parents = [f"{x.original_resource_type};name;{x.original_resource_name}" for x in events]
        all_parents = event_parents + config_parents + permissions_parents
        self.parents = all_parents
        log.info(f"ALL PARENTS {self.parents}")


    def render(self) -> simple_aws_lambda_function_model:
       
        return simple_aws_lambda_function_model(**{
            "name": self.name,
            "ruuid": "cdev::simple::lambda_function",
            "hash": self.full_hash,
            "filepath": self.filepath,
            "events": self.events,
            "permissions": self.permissions,
            "configuration": self.configuration,
            "permissions_hash": self.permissions_hash,
            "src_code_hash": self.src_code_hash,
            "config_hash": self.config_hash,
            "events_hash": self.events_hash,
            "parent_resources": self.parents
        })
        

    def get_includes(self) -> List[str]:
        return self.includes




def simple_lambda_function_annotation(name, includes: List[str]=[], events: List[Event]=[],  Environment={}, permissions: List[Union[Permission,PermissionArn]]=[]):
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
                    function_name=item[1]
                elif item[0] == "__doc__":
                    description = item[1] if item[1] else ""
                elif item[0] == "__module__":
                    mod_name = item[1]
                #elif item[0] == "__code__":
                #    code_prop_names = set(["co_varnames", "co_argcount", "co_posonlyargcount"])
                    #code_props = [(z[0],z[1]) for z in inspect.getmembers(item[1]) if z[0] in code_prop_names]

                    #is_valid_signature = True

                    #for prop in code_props:
                    #    if prop[0] == "co_argcount":
                    #        if not prop[1] == 2:
                    #            is_valid_signature = False
                    #            print(f'bad sig argcnt {prop[1]}')
                    #            break
                    #    elif prop[0] == "co_posonlyargcount":
                    #        if not prop[1] == 2:
                    #            is_valid_signature = False
                    #            print(f'bad sig poscnt -> {prop[1]}')
                    #    elif prop[0] == "co_varnames":
                    #        if not ("context" in prop[1] and "event" in prop[1]):
                    #            is_valid_signature = False
                    #            print(f'bad sig names')
                    #            break

        base_config = {
        
        }

        base_config["Environment"] = {"Variables": Environment} if Environment else None
        base_config["Description"] = description
        base_config["Handler"] = function_name


        final_config = lambda_function_configuration(**base_config)

        mod = importlib.import_module(mod_name)

        full_filepath = os.path.abspath(mod.__file__)
                    
        return simple_lambda(cdev_name=name, filepath=full_filepath, events=events, configuration=final_config, permissions=permissions ,includes=includes)

    
   
    return create_function
        





