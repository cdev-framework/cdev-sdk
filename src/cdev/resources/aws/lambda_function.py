from enum import Enum
import inspect
import importlib
import os
from pathlib import PosixPath, WindowsPath
from pydantic import BaseModel, FilePath, conint
from typing import List, Union, Dict, Optional

from ...models import Rendered_Resource
from ...utils import hasher, paths

from .s3 import s3_object


def lambda_function_annotation(name, events=[], includes=[], Enivornment={},  Role:str=None, Timeout:conint(gt=1,lt=300)=None, MemorySize:conint(gt=1,lt=1024)=None ):
    """
    This annotation is used to designate that a function should be deployed on the AWS lambda platform. Functions that are designated
    using this annotation should have a signature that takes two inputs (event,context) to conform to the aws lambda handler signature.

    Functions that are annotated with this symbol will be put through the cdev function parser to optimize the final deployed artifact
    to only contain global statements needed for this function. For more information on this process read <link>.

    """

    events = events if events else [""]

    EnvironmentVars =  {"Variables": Enivornment} if Enivornment else None


    base_config = {
        "Role": Role,
        "Timeout": Timeout,
        "MemorySize": MemorySize,
        "Environment": EnvironmentVars
    }

    def wrap_create_function(func):
        
        def create_function(*args, **kwargs) -> aws_lambda_function:  

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

            base_config["Description"] = description
            base_config["Runtime"] = lambda_runtime_environments.python3_6
            base_config["Handler"] = function_name


            final_config = lambda_function_configuration(**base_config)

            mod = importlib.import_module(mod_name)

            full_filepath = os.path.abspath(mod.__file__)
           
            rv_func = aws_lambda_function(**{
                "FunctionName": name,
                "Configuration": final_config,
                "FPath": full_filepath,
                "name": name,
                "ruuid": "cdev::aws::lambdafunction",
                "hash": hasher.hash_list([hasher.hash_file(full_filepath), name]),
                "events": events
            })
                        
            return rv_func

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
    Role: Union[str,None]
    Handler: Union[str,None]
    Description: Union[str,None]
    Timeout: Union[conint(gt=1,lt=300),None]
    MemorySize: Union[conint(gt=1,lt=1024),None]
    Environment: Union[Dict,None]
    Runtime: Union[lambda_runtime_environments,None]

    def __init__(__pydantic_self__, Role: str="", Handler: str="", Description: str="", Timeout: int=60,
                MemorySize: int=128, Environment: lambda_function_configuration_environment={}, 
                Runtime: lambda_runtime_environments="python3.6" ) -> None:
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
    Configuration: lambda_function_configuration
    FPath: str # Don't use FilePath because this will be a relative path and might not always point correctly to a file in all contexts

    def __init__(__pydantic_self__, FunctionName: str, Configuration: lambda_function_configuration, FPath: FilePath, **kwargs) -> None:
        if kwargs:
            kwargs.update(**{
                "FunctionName": FunctionName,
                "Configuration": Configuration,
                "FPath": FPath
            })
            super().__init__(**kwargs)
        else:
            return None

    class Config:
        json_encoders = {
            PosixPath: lambda v: v.as_posix(), # or lambda v: str(v)
            WindowsPath: lambda v: v.as_posix()
        }

        extra='ignore'
