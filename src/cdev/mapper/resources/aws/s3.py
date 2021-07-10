from typing import List, Union
from pydantic import BaseModel, FilePath, conint


class s3_object(BaseModel):
    S3Bucket: str
    S3Key: str
