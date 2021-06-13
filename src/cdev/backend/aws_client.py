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