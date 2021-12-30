from typing import List, Union
from pydantic import BaseModel

from enum import Enum

class aws_credentials_type(str, Enum):
    raw_credentials="raw_credentials"
    profile="profile"


class aws_key(BaseModel):
    access_key: str
    secret_key: str


class aws_credentials(BaseModel):
    credentials_type: aws_credentials_type
    value: Union[aws_key, str]
