from typing import Tuple, List

from pydantic import DirectoryPath
from cdev.utils.git_safe.utils import get_repo, create_repo


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

    if is_config_setup:
        print(f"Config is already set up correctly")
        return

    # If configuration does not exist, write the configuration
    config_writer = repo.config_writer()
    for configuration in configurations:
        config_writer.set_value(configuration_name, configuration[0], configuration[1])

    config_writer.release()


def _get_configuration_information() -> Tuple[str, List[str]]:
    _configs = [
        (
            "name",
            "A custom merge driver used to resolve conflicts in cdev_project.json",
        ),
        ("driver", "cdev git-safe project-merger %A %B"),
    ]  # %A -> Current File; %B -> Other Commit File

    return ("merge.cdev-project-drive", _configs)
