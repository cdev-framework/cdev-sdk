from time import sleep
from typing import Callable, List
import boto3

from core import settings as cdev_settings
from core.utils import logger

AVAILABLE_SERVICES = set(["lambda", "s3", "dynamodb", "iam", "apigatewayv2", "sqs", "apigateway"])


log = logger.get_cdev_logger(__name__)

def _get_boto_client(service_name, credentials=None, profile_name=None):

    # TODO readd this check after development is finished and we have the full list of services
    #if not service_name in AVAILABLE_SERVICES:
    #    return None

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


def monitor_status(func: Callable, params: dict, previous_val, lookup_func: Callable) -> dict: 
    """
    This function is used to monitor the status of resources as they are created by aws. Alot of resources are created
    asynchronously by aws, which means the original create call returns before the actual resource is created. Therefor,
    we use this function to handle repeatedly calling a status function to check if the resource was created.   
    """

    MAX_RESOURCE_TIME = 600
    HEARTBEAT_PACE = 10

    loops = int(MAX_RESOURCE_TIME/HEARTBEAT_PACE)
    log.debug(f"WAITING FOR CHANGE OF VALUE {previous_val}")

    for _ in range(loops):
        rv = func(**params)

        if rv.get("ResponseMetadata").get("HTTPStatusCode") == 200:
            new_value = lookup_func(rv)
            log.debug(new_value)
            if not new_value == previous_val:
                log.debug(f"FINISHED {new_value}")
                return rv
        
        log.debug("HEARTBEAT")
        sleep(HEARTBEAT_PACE)       


    return None


def run_client_function(service: str, function_name: str, args: dict, wait: dict = None):
    args_as_string = f"({service}, {function_name}, {args}, {wait})"
    log.debug(f"Attempting to call aws -> {args_as_string}")
    rendered_client = _get_boto_client(service)
    method = getattr(rendered_client, function_name)

    if method:
        rv = method(**args)
        log.debug(f"AWS {args_as_string} -> {rv}")

    if wait:
        waiter = rendered_client.get_waiter(wait.get("name"))
        final_args = {
            "WaiterConfig":
                {
                    'Delay': 10,
                    'MaxAttempts': 60
                }
        }
        final_args.update( wait.get("args") )
        
        log.debug(f"Begin wait {args_as_string} -> {final_args}")
        waiter.wait(**final_args)
        log.debug(f"Finish wait {args_as_string} -> {final_args}")

    return rv


def aws_resource_wait(service: str, wait: dict):
    rendered_client = _get_boto_client(service)
    waiter = rendered_client.get_waiter(wait.get("name"))
    final_args = {
        "WaiterConfig":
            {
                'Delay': 10,
                'MaxAttempts': 60
            }
    }
    final_args.update( wait.get("args") )
    
    log.debug(f"Begin wait {final_args}")
    waiter.wait(**final_args)
    log.debug(f"Finish wait {final_args}")


    


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
