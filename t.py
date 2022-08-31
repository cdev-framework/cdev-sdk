from typing import *
from rich.prompt import Prompt, Confirm
from rich import print

from dataclasses import dataclass


@dataclass
class aws_configuration:
    access_key: str
    secret_key: str
    region_name: str


def _prompt_new_cloud_configuration() -> Optional[Dict[str, str]]:
    _current_credentials = _get_current_credentials()
    if _current_credentials:
        if _prompt_use_same_configuration(_current_credentials):
            return None

    _credentials_explanation()
    return _prompt_credentials()


def _credentials_explanation():
    print(f"Enter your Aws Credentials")
    print("")


def _prompt_credentials() -> Dict[str, str]:

    _access_key = Prompt.ask("AWS Access Key ID")
    _secret_key = Prompt.ask("AWS Secret Key ID")
    _region_name = Prompt.ask("Default region name")

    return aws_configuration(
        access_key=_access_key, secret_key=_secret_key, region_name=_region_name
    )


def _prompt_use_same_configuration(current_configuration: Dict = {}) -> bool:

    print("Your current Aws Credentials are:")
    for k, v in current_configuration.items():
        print(f"  {k} -> {v}")

    print("")
    return Confirm.ask("Would you like to continue using the found credentials?")


def _get_current_credentials() -> Optional[Dict]:
    return None
    # return {
    #    'Aws Access Key ID': 'asdas',
    #    'Aws Secret Access Key': 'asd',
    #    'Default region name': 'wef',
    # }


data = _prompt_new_cloud_configuration()
print(data)
