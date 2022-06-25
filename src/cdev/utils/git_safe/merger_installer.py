import os
from cdev.utils.git_safe.utils import get_repo, create_repo


def install_custom_merger() -> None:
    _base_dir = os.getcwd()
    # Check if there is a git repo
    repo = get_repo(dir=_base_dir) or create_repo(dir=_base_dir)

    if not repo:
        print("no repo")
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


def _get_configuration_information() -> None:
    _configs = [
        ("name", "A custom merge driver used to resolve conflicts i"),
        ("driver", "python demo.py %O %A %B %P"),
    ]

    return ("merge.cdev-project-drive", _configs)
