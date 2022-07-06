from typing import Tuple, List

from pydantic import DirectoryPath
from cdev.utils.git_safe.utils import get_repo, create_repo
from core.utils.paths import touch_file

import os


def install_custom_merger(_base_dir: DirectoryPath) -> None:
    # Check if there is a git repo
    repo = get_repo(
        dir=_base_dir
    )  # or create_repo(dir=_base_dir) # Readd later with dialogue to confirm they want to init a git project

    if not repo:
        print(f"no git project at {repo}")
        return

    # Get the configuration information
    configuration_name, configurations = _get_configuration_information()

    # Check if the configuration information already exist
    config_reader = repo.config_reader()

    try:
        is_config_setup = all(
            [
                config_reader.get_value(configuration_name, x[0]) == x[1]
                for x in configurations
            ]
        )
    except Exception:
        is_config_setup = False

    if not is_config_setup:
        # If configuration does not exist, write the configuration
        config_writer = repo.config_writer()
        for configuration in configurations:
            config_writer.set_value(
                configuration_name, configuration[0], configuration[1]
            )

        config_writer.release()

    # Check if the project currently has the gitattributes set
    _check_or_make_local_attributes(_base_dir)
    _needed_attribute = _get_git_attribute_information()

    _add_git_attribute(_base_dir, _needed_attribute)


def _check_or_make_local_attributes(base_dir: DirectoryPath) -> None:
    if not os.path.isdir(base_dir):
        raise Exception

    _attribute_location = os.path.join(base_dir, ".gitattributes")

    if os.path.isfile(_attribute_location):
        return
    else:
        touch_file(_attribute_location)


def _add_git_attribute(base_dir: DirectoryPath, attributes: List[str]) -> None:
    _attribute_location = os.path.join(base_dir, ".gitattributes")

    _current_attributes = open(_attribute_location).readlines()

    if not _current_attributes:
        _needed_attributes = attributes

    else:
        _needed_attributes = list(set(attributes).difference(set(_current_attributes)))

    _current_attributes.extend(_needed_attributes)

    with open(_attribute_location, "w") as fh:
        fh.writelines(_current_attributes)


def _get_configuration_information() -> Tuple[str, List[str]]:
    _configs = [
        (
            "name",
            "A custom merge driver used to resolve conflicts in cdev_project.json",
        ),
        ("driver", "cdev git-safe project-merger %A %B"),
    ]  # %A -> Current File; %B -> Other Commit File

    return ("merge.cdev-project-drive", _configs)


def _get_git_attribute_information() -> List[str]:
    return [".cdev/cdev_project.json merge=cdev-project-drive"]
