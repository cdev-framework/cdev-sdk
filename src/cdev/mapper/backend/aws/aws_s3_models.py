from logging import FileHandler
from typing import Any, List, Union
from pydantic import BaseModel, FilePath, conint

from cdev.resources.aws import s3, lambda_function


class put_object_event(BaseModel):
    Filename: str
    Bucket: str
    Key: str