from time import sleep
from typing import Callable, List
import boto3

from cdev import settings as cdev_settings

AVAILABLE_SERVICES = set(["lambda", "s3", "dynamodb"])


def _get_boto_client(service_name, credentials=None, profile_name=None):

    if not service_name in AVAILABLE_SERVICES:
        return None

    if not credentials or not profile_name:
        return boto3.client(service_name)

    if credentials:
        return boto3.Session(
            aws_access_key_id=credentials.get("access_key"),
            aws_secret_access_key=credentials.get("secret_key")
        ).client(service_name)

    if profile_name:
        return boto3.Session(
            profile_name=profile_name
        ).client(service_name)


def get_boto_client(service_name):
    if not cdev_settings.SETTINGS.get("CREDENTIALS"):
        return _get_boto_client(service_name)

    if cdev_settings.SETTINGS.get("CREDENTIALS").get("credentials_type") == "raw_credentials":
        return _get_boto_client(service_name, credentials=cdev_settings.SETTINGS.get("CREDENTIALS").get("value"))

    if cdev_settings.SETTINGS.get("CREDENTIALS").get("credentials_type") == "profile":
        return _get_boto_client(service_name, profile_name=cdev_settings.SETTINGS.get("CREDENTIALS").get("value"))


def monitor_status(func: Callable, params: dict, previous_val, lookup_keys: List) -> dict: 
    """
    This function is used to monitor the status of resources as they are created by aws. Alot of resources are created
    asynchronously by aws, which means the original create call returns before the actual resource is created. Therefor,
    we use this function to handle repeatedly calling a status function to check if the resource was created.   
    """

    MAX_RESOURCE_TIME = 30
    HEARTBEAT_PACE = 2

    loops = int(MAX_RESOURCE_TIME/HEARTBEAT_PACE)
    print(f"WAITING FOR CHANGE OF VALUE {previous_val}")

    for _ in range(loops):
        rv = func(**params)

        tmp_keys = list(lookup_keys)
        if rv.get("ResponseMetadata").get("HTTPStatusCode") == 200:
            new_value = _recursive_find_key(rv, tmp_keys)
            if not new_value == previous_val:
                return rv
        
        print("HEARTBEAT")
        sleep(HEARTBEAT_PACE)       

    return None

        

def _recursive_find_key(d: dict, keys: List):
    if len(keys) == 0:
        return None

    if len(keys) == 1:
        return d.get(keys[0])

    else:
        top_key = keys[0]
        keys.pop(0)

        if not top_key in d:
            return None

        return _recursive_find_key(d.get(top_key), keys)

