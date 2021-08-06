from pathlib import PosixPath, WindowsPath
from typing import List, Union, Dict, Optional
from pydantic import BaseModel, FilePath, conint

from cdev.models import Rendered_Resource


class pre_parsed_serverless_function(BaseModel):
    name: str
    handler_name: str
    description: str
    configuration: dict
    permissions: Optional[list]

    def __init__(__pydantic_self__, name: str, handler_name: str, description: str, configuration: dict, **kwargs) -> None:
        if kwargs:
            kwargs.update({
                "name": name,
                "handler_name": handler_name,
                "description": description,
                "configuration": configuration
            })
            super().__init__(**kwargs)

        else:
            super().__init__(**{
                "name": name,
                "handler_name": handler_name,
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

    permissions: Optional[List]

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
