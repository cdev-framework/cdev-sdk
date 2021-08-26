from enum import Enum
from typing import Dict, List, Union

from pydantic.main import BaseModel
from pydantic import FilePath
from ...models import Rendered_Resource, Cloud_Output

from sortedcontainers.sorteddict import SortedDict

import importlib
import inspect
import os

from pathlib import PosixPath, WindowsPath
from cdev.utils import hasher

class EventTypes(Enum):
    HTTP_API_ENDPOINT = "api::endpoint"


class Event(BaseModel):
    original_resource_id: str

    event_type: EventTypes

    config: Dict




def simple_lambda_function_annotation(name, includes=[], events: List[Event]=[],  Environment={}):
    """
    This annotation is used to designate that a function should be deployed on the AWS lambda platform. Functions that are designated
    using this annotation should have a signature that takes two inputs (event,context) to conform to the aws lambda handler signature.

    Functions that are annotated with this symbol will be put through the cdev function parser to optimize the final deployed artifact
    to only contain global statements needed for this function. For more information on this process read <link>.

    """

    events = events if events else [""]

    EnvironmentVars =  {"Variables": Environment} if Environment else None


    base_config = {
        "Environment": EnvironmentVars
    }

    def wrap_create_function(func):
        
        def create_function(*args, **kwargs) -> simple_aws_lambda_function_model:  

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

            base_config["Description"] = description
            base_config["Handler"] = function_name


            final_config = lambda_function_configuration(**base_config)

            

            mod = importlib.import_module(mod_name)

            full_filepath = os.path.abspath(mod.__file__)

            src_code_hash = hasher.hash_file(full_filepath)
            config_hash = final_config.get_cdev_hash()
           
            rv_func = simple_aws_lambda_function_model(**{
                "FunctionName": name,
                "Configuration": final_config,
                "FPath": full_filepath,
                "name": name,
                "ruuid": "cdev::simple::lambdafunction",
                "hash": hasher.hash_list([src_code_hash, config_hash]),
                "events": events,
                "src_code_hash": src_code_hash,
                "config_hash": config_hash,
            })
                        
            return rv_func

        return create_function
    
    return wrap_create_function
        

class simple_aws_lambda_function_model(Rendered_Resource):
    """
    An aws lambda function
    """

    FunctionName: str
    FPath: str # Don't use FilePath because this will be a relative path and might not always point correctly to a file in all contexts

    src_code_hash: str
    config_hash: str

    def __init__(__pydantic_self__, FunctionName: str,  FPath: FilePath, src_code_hash: str, config_hash: str, **kwargs) -> None:
        parents = set()

        if kwargs:
            kwargs.update(**{
                "FunctionName": FunctionName,
                "FPath": FPath,
                "src_code_hash": src_code_hash,
                "config_hash": config_hash,
                "parent_resources": list(parents),
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


    def __init__(__pydantic_self__,  Handler: str="", Description: str="") -> None:
        super().__init__(**{
            "Handler": Handler,
            "Description": Description,

        })

    def get_cdev_hash(self) -> str:
        if self.Environment:
            env_hash = self.Environment.get_cdev_hash()
        else: 
            env_hash = ""
        rv = hasher.hash_list([self.Description, env_hash, self.Handler])
        return rv

