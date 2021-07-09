import inspect
from pathlib import PosixPath, WindowsPath
from typing import List, Union
from pydantic import BaseModel, FilePath, conint
from enum import Enum

from cdev.models import Rendered_Resource

from .s3 import s3_object


def lambda_function_annotation(name, events={}, configuration={}, includes=[]):
    """
    This annotation is used to designate that a function should be deployed on the AWS lambda platform. Functions that are designated
    using this annotation should have a signature that takes two inputs (event,context) to conform to the aws lambda handler signature.

    Functions that are annotated with this symbol will be put through the cdev function parser to optimize the final deployed artifact
    to only contain global statements needed for this function. For more information on this process read <link>.

    """

    events = events if events else [""]

    configuration =  configuration if configuration else {"v":"s"}

    def wrap_create_function(func):
        
        def create_function(*args, **kwargs) -> pre_parsed_serverless_function:  

            if inspect.isfunction(func):
                for item in inspect.getmembers(func):
                    
                    if item[0] == "__name__":
                        function_name=item[1]
                    elif item[0] == "__doc__":
                        description = item[1] if item[1] else ""
                    #elif item[0] == "__code__":
                    #    code_prop_names = set(["co_varnames", "co_argcount", "co_posonlyargcount"])
                        #code_props = [(z[0],z[1]) for z in inspect.getmembers(item[1]) if z[0] in code_prop_names]

                        #is_valid_signature = True
#
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

                    
                        
            rv = pre_parsed_serverless_function( **{
                "name": name,
                "handler_name": function_name,
                "events": events,
                "description": description,
                "configuration": configuration
            })

            return rv

        return create_function
    
    return wrap_create_function




class lambda_runtime_environments(str,Enum):
    python3_6="python3.6"
    python3_7="python3.7"
    python3_8="python3_8"


class lambda_function_configuration_environment(BaseModel):
    Variables: dict


class lambda_function_configuration(BaseModel):
    Role: str
    Handler: str
    Description: str
    Timeout: conint(gt=1,lt=300)
    MemorySize: conint(gt=1,lt=1024)
    Environment: lambda_function_configuration_environment
    Runtime: lambda_runtime_environments
    Layers: List[str]


class aws_lambda_function(Rendered_Resource):
    FunctionName: str
    Code: s3_object
    Configuration: lambda_function_configuration



class pre_parsed_serverless_function(BaseModel):
    name: str
    handler_name: str
    events: List[str]
    description: str 
    configuration: dict
    

class parsed_serverless_function_info(pre_parsed_serverless_function):
    needed_lines: List[List[int]]
    dependencies: Union[List[str], None]


class parsed_serverless_function_resource(Rendered_Resource):
    original_path: FilePath
    parsed_path: FilePath
    source_code_hash: str
    handler_name: str

    dependencies: Union[List[str], None]
    dependencies_hash: str

    configuration: dict

    identity_hash: str

    metadata_hash: str

    class Config:
        json_encoders = {
            PosixPath: lambda v: v.as_posix(), # or lambda v: str(v)
            WindowsPath: lambda v: v.as_posix()
        }

        extra='ignore'
