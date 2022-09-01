from typing import *
import os
from rich.prompt import Prompt, Confirm
from rich import print
from configparser import ConfigParser

from dataclasses import dataclass, fields

from pathlib import Path


@dataclass
class aws_configuration:
    access_key: str
    secret_key: str
    region_name: str


_base_dir = Path.home()
_credentials_location = ".aws/credentials"
_config_location = ".aws/config"

_full_credential_location = os.path.join(_base_dir, _credentials_location)
_full_config_location = os.path.join(_base_dir, _config_location)

_default_name = "default"
_access_key_id = "aws_access_key_id"
_secret_key_id = "aws_secret_access_key"
_region_id = "region"


def _prompt_new_cloud_configuration() -> Optional[Dict[str, str]]:
    _current_credentials = _get_current_credentials()
    if _current_credentials:
        if _prompt_use_same_configuration(_current_credentials):
            return None

    if not _prompt_ask_credentials():
        return None

    _credentials_explanation()
    return _prompt_credentials()


def _prompt_ask_credentials():
    return Confirm.ask("Would you like to set your Aws Credentials?")


def _credentials_explanation():
    print("")
    print("Enter your Aws Credentials")


def _prompt_credentials() -> Dict[str, str]:

    _access_key = Prompt.ask("AWS Access Key ID")
    _secret_key = Prompt.ask("AWS Secret Key ID")
    _region_name = Prompt.ask("Default region name")

    return aws_configuration(
        access_key=_access_key, secret_key=_secret_key, region_name=_region_name
    )


def _prompt_use_same_configuration(
    current_configuration: aws_configuration = {},
) -> bool:
    print("Your current Aws Credentials are:")
    for field in fields(current_configuration):
        print(f"{field.name} -> {getattr(current_configuration, field.name)}")

    print("")
    return Confirm.ask("Would you like to continue using the found credentials?")


def _get_current_credentials() -> Optional[Dict]:
    if not (
        os.path.isfile(_full_credential_location)
        and os.path.isfile(_full_config_location)
    ):
        return None

    credentials_config = ConfigParser()
    credentials_config.read(_full_credential_location)

    if (
        len(credentials_config.sections()) == 0
        or not _default_name in credentials_config
    ):
        return None

    default_credentials_config = credentials_config[_default_name]
    if not (
        _access_key_id in default_credentials_config
        and _secret_key_id in default_credentials_config
    ):
        return None

    config_config = ConfigParser()
    config_config.read(_full_config_location)

    if len(config_config.sections()) == 0 or not _default_name in credentials_config:
        return None

    default_config_config = config_config[_default_name]

    if not _region_id in default_config_config:
        return None

    return aws_configuration(
        access_key=__star_out(default_credentials_config[_access_key_id]),
        secret_key=__star_out(default_credentials_config[_secret_key_id]),
        region_name=default_config_config[_region_id],
    )


def _write_default_credentials(credentials: aws_configuration):
    credentials_config = ConfigParser()
    credentials_config.read(_full_credential_location)

    config_config = ConfigParser()
    config_config.read(_full_config_location)

    credentials_config[_default_name][_access_key_id] = credentials.access_key
    credentials_config[_default_name][_secret_key_id] = credentials.secret_key
    config_config[_default_name][_region_id] = credentials.region_name

    with open(_full_credential_location, "w") as fh_credentials, open(
        _full_config_location, "w"
    ) as fh_config:
        credentials_config.write(fh_credentials)
        config_config.write(fh_config)


def __star_out(s: str, remaining: int = 4, max_char: int = 16) -> str:
    star_length = min(len(s) - remaining, max_char)
    return ("*" * star_length) + s[-remaining:]


def prompt_write_default_aws_credentials():
    data = _prompt_new_cloud_configuration()
    if data:
        try:
            _write_default_credentials(credentials=data)
        except Exception as e:
            print(
                "Error saving your credentials. Use the aws command tool to set your credentials."
            )

        print("Saved Credentials ✔️")
