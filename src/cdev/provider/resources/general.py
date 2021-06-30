from typing import List, Union
from pydantic import BaseModel, FilePath
from sortedcontainers.sortedlist import identity

from cdev.frontend.models import Rendered_Resource

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

