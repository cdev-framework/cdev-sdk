from . import aws_client
from .aws_s3_models import *

client = aws_client.get_boto_client("s3")

def put_object(put_object_event: put_object_event) -> bool:
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_file


    """
    try:
        client.upload_file(**put_object_event.dict())
    except Exception as e:
        print(e)
        return False
