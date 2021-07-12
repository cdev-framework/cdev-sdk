import inspect
from pathlib import PosixPath, WindowsPath
from typing import List, Union, Dict
from pydantic import BaseModel, FilePath, conint
from enum import Enum

from pydantic.errors import EnumError

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

    configuration =  configuration if configuration else {"ve":"se"}

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

    def __init__(__pydantic_self__, Variables: Dict) -> None:
        super().__init__(**{
            "Variables": Variables
        })


class lambda_function_configuration(BaseModel):
    Role: str
    Handler: str
    Description: str
    Timeout: conint(gt=1,lt=300)
    MemorySize: conint(gt=1,lt=1024)
    Environment: Dict
    Runtime: lambda_runtime_environments

    def __init__(__pydantic_self__, Role: str, Handler: str, Description: str, Timeout: int,
                MemorySize: int, Environment: lambda_function_configuration_environment, 
                Runtime: lambda_runtime_environments ) -> None:
        super().__init__(**{
            "Role": Role,
            "Handler": Handler,
            "Description": Description,
            "Timeout": Timeout,
            "MemorySize": MemorySize,
            "Environment": Environment,
            "Runtime": Runtime,
        })


class aws_lambda_function(Rendered_Resource):
    FunctionName: str
    Code: s3_object
    Configuration: lambda_function_configuration

    def __init__(__pydantic_self__, FunctionName: str, Code: s3_object, Configuration: lambda_function_configuration) -> None:
        super().__init__(**{
            "FunctionName": FunctionName,
            "Code": Code,
            "Configuration": Configuration
        })



class pre_parsed_serverless_function(BaseModel):
    name: str
    handler_name: str
    events: List[str]
    description: str 
    configuration: dict

    def __init__(__pydantic_self__, name: str, handler_name: str, events: List[str], description: str, configuration: dict, **kwargs) -> None:
        if kwargs:
            kwargs.update({
                "name": name,
                "handler_name": handler_name,
                "events": events,
                "description": description,
                "configuration": configuration
            })
            super().__init__(**kwargs)

        else:
            super().__init__(**{
                "name": name,
                "handler_name": handler_name,
                "events": events,
                "description": description,
                "configuration": configuration
            })
    

class parsed_serverless_function_info(pre_parsed_serverless_function):
    needed_lines: List[List[int]]
    dependencies: Union[List[str], None]

    def __init__(__pydantic_self__, needed_lines: List[List[str]], dependencies: List[str], **kwargs) -> None:
        if kwargs:
            kwargs.update({
                "needed_lines": needed_lines,
                "dependencies": dependencies
            })
            super().__init__(**kwargs)
        else:
            super().__init__(**{
                "needed_lines": needed_lines,
                "dependencies": dependencies
            })


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

    def __init__(__pydantic_self__, original_path: FilePath, parsed_path: FilePath, source_code_hash: str, handler_name: str,
                dependencies: List[str], dependencies_hash: str, configuration: Dict, identity_hash: str, metadata_hash: str, **kwargs) -> None:
        
        if kwargs:
            kwargs.update({
            "original_path": original_path,
            "parsed_path": parsed_path,
            "source_code_hash": source_code_hash,
            "handler_name": handler_name,
            "dependencies": dependencies,
            "dependencies_hash": dependencies_hash,
            "configuration": configuration,
            "identity_hash": identity_hash,
            "metadata_hash": metadata_hash
            })
            super().__init__(**kwargs)
        
        else:   
            super().__init__(**{
                "original_path": original_path,
                "parsed_path": parsed_path,
                "source_code_hash": source_code_hash,
                "handler_name": handler_name,
                "dependencies": dependencies, 
                "configuration": configuration,
                "identity_hash": identity_hash,
                "metadata_hash": metadata_hash
            })
