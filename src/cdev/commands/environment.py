from rich.prompt import Confirm
from typing import List, Tuple

from core.constructs.output_manager import OutputManager

from cdev.constructs.project import Project
from cdev.default.output_manager import CdevOutputManager
from cdev.cli.logger import set_global_logger_from_cli


def environment_cli(args) -> None:
    command = args[0]
    parsed_args = vars(args[1])

    set_global_logger_from_cli(parsed_args.get("loglevel"))
    output_manager = CdevOutputManager()

    if command == "":
        output_manager._console.print(
            "You must provide a sub-command. run `cdev environment --help` for more information on available subcommands"
        )
    elif command == "ls":
        list_environments(output_manager)
    elif command == "get":
        pass
    elif command == "set":
        set_current_environment(parsed_args.get("env"), output_manager)
    elif command == "create":
        create_environment(parsed_args.get("env"), output_manager)
    elif command == "settings_information":
        settings_information(
            output_manager,
            parsed_args.get("key"),
            parsed_args.get("new_value"),
            parsed_args.get("all"),
        )


def list_environments(output: OutputManager) -> None:
    """
    Get the current list of environments and the current environment from the Project object.
    Must be called when the Project is in the UNINITIALIZED phase.
    """

    myProject = Project.instance()

    current_environment_name = myProject.get_current_environment_name()
    all_environment_names = myProject.get_all_environment_names()

    for environment_name in all_environment_names:
        if current_environment_name == environment_name:
            output._console.print(f"> {environment_name}")
        else:
            output._console.print(environment_name)


def set_current_environment(
    new_current_environment: str, output: OutputManager
) -> None:
    myProject = Project.instance()

    try:
        myProject.set_current_environment(new_current_environment)
    except Exception as e:
        output._console.print(
            f"Could not set {new_current_environment} as the environment"
        )
        return

    output._console.print(f"Set Current Environment -> {new_current_environment}")


def create_environment(new_environment_name: str, output: OutputManager) -> None:
    myProject = Project.instance()

    myProject.create_environment(new_environment_name)

    output._console.print(f"Created Environment -> {new_environment_name}")


def settings_information(
    output: OutputManager,
    key: str = None,
    new_value: str = None,
    all: bool = False,
) -> None:
    myProject = Project.instance()

    if all and not new_value:
        raise Exception("Must use --all with --new-value")

    if not new_value:
        settings_info = myProject.get_environment_settings_info()
        settings_dict = settings_info.dict()
        output._console.print(
            f"Settings info for Environment {myProject.get_current_environment_name()}:"
        )
        if key:
            # Print desired key
            if key not in settings_dict:
                raise Exception(
                    f"Key {key} not in settings information {settings_info}"
                )

            output._console.print(f"    {key} -> {settings_dict.get(key)}")
        else:
            # Print all values
            for key, value in settings_dict.items():
                output._console.print(f"    {key} -> {value}")

    else:
        if not key:
            raise Exception("Must use --new-value with --key")

        if not all:
            settings_info = myProject.get_environment_settings_info()

            did_confirm = output._console.input(
                f"Are you sure you want to update {key} to {new_value} for the current environment ({myProject.get_current_environment_name()}) \[y/n]?: "
            )

            if did_confirm != "y":
                output._console.print("Did not confirm. Aborting operation.")
                return

            setattr(settings_info, key, new_value)

            myProject.update_environment_settings_info(settings_info)
            output._console.print(f"Updated {key} -> {new_value}")

        else:
            did_confirm = output._console.input(
                f"Are you sure you want to update {key} to {new_value} for all environments \[y/n]?: "
            )
            if did_confirm != "y":
                output._console.print("Did not confirm. Aborting operation.")
                return

            for environment_name in myProject.get_all_environment_names():
                settings_info = myProject.get_environment_settings_info(
                    environment_name
                )

                setattr(settings_info, key, new_value)

                myProject.update_environment_settings_info(
                    settings_info, environment_name
                )
                output._console.print(
                    f"Updated ({environment_name}) {key} -> {new_value}"
                )
