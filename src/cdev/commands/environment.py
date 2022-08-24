from argparse import Namespace

from cdev.constructs.project import EnvironmentDoesNotExist, Project, ProjectError

from core.constructs.output_manager import OutputManager


def environment_cli(
    command: str,
    parsed_args_namespace: Namespace,
    output_manager: OutputManager,
    project: Project,
    **kwargs,
) -> None:

    parsed_args = vars(parsed_args_namespace)

    if command == "":
        output_manager._console.print(
            "You must provide a sub-command. run `cdev environment --help` for more information on available subcommands"
        )
    elif command == "ls":
        list_environments(project, output_manager)
    elif command == "info":
        environment_information(project, output_manager, parsed_args.get("env"))
    elif command == "set":
        set_current_environment(project, parsed_args.get("env"), output_manager)
    elif command == "create":
        create_environment(project, parsed_args.get("env"), output_manager)
    elif command == "settings_information":
        settings_information(
            project,
            output_manager,
            parsed_args.get("key"),
            parsed_args.get("new_value"),
            parsed_args.get("all"),
        )


def list_environments(project: Project, output: OutputManager) -> None:
    """
    Get the current list of environments and the current environment from the Project object.
    Must be called when the Project is in the UNINITIALIZED phase.
    """

    current_environment_name = project.get_current_environment_name()
    all_environment_names = project.get_all_environment_names()

    for environment_name in all_environment_names:
        if current_environment_name == environment_name:
            output._console.print(f"> {environment_name}")
        else:
            output._console.print(environment_name)


def set_current_environment(
    project: Project, new_current_environment: str, output: OutputManager
) -> None:
    """Change the current environment of the project

    Args:
        new_current_environment (str): new current environment name
        output (OutputManager): Output manager
    """

    try:
        project.set_current_environment(new_current_environment)
    except EnvironmentDoesNotExist as e:
        output._console.print(
            f"Environment {new_current_environment} does not exist in this project"
        )
        return
    except Exception as e:
        output._console.print(
            f"Uncaught Exception {e} when trying to change current environment"
        )
        return

    output._console.print(f"Set Current Environment -> {new_current_environment}")


def create_environment(
    project: Project, new_environment_name: str, output: OutputManager
) -> None:
    project.create_environment(new_environment_name)

    output._console.print(f"Created Environment -> {new_environment_name}")


def settings_information(
    project: Project,
    output: OutputManager,
    key: str = None,
    new_value: str = None,
    all: bool = False,
) -> None:
    _environment_name = project.get_current_environment_name()

    if not new_value:
        settings_info = project.get_environment_settings_info(_environment_name)
        settings_dict = settings_info.dict()
        if key:
            # Print desired key
            if key not in settings_dict:
                raise Exception(
                    f"Key ({key}) not in settings information for the Environment: {_environment_name}"
                )
            output._console.print(f"Environment Settings: {_environment_name}")
            output._console.print(f"    {key} -> {settings_dict.get(key)}")
        else:
            # Print all values
            output._console.print(
                f"Current Settings info for Environment: {_environment_name}:"
            )
            for key, value in settings_dict.items():
                output._console.print(f"    {key} -> {value}")

    else:
        if not key:
            raise Exception("Must use --new-value with --key")

        if not all:
            settings_info = project.get_environment_settings_info(_environment_name)

            did_confirm = output._console.input(
                f"Are you sure you want to update {key} to {new_value} for the environment ({_environment_name}) \[y/n]?: "
            )

            if did_confirm != "y":
                output._console.print("Did not confirm. Aborting operation.")
                return

            setattr(settings_info, key, new_value)

            project.update_environment_settings_info(
                new_value=settings_info, environment_name=_environment_name
            )
            output._console.print(f"Updated {key} -> {new_value}")

        else:
            did_confirm = output._console.input(
                f"Are you sure you want to update {key} to {new_value} for all environments in the project \[y/n]?: "
            )
            if did_confirm != "y":
                output._console.print("Did not confirm. Aborting operation.")
                return

            for environment_name in project.get_all_environment_names():
                settings_info = project.get_environment_settings_info(environment_name)

                setattr(settings_info, key, new_value)

                project.update_environment_settings_info(
                    new_value=settings_info, environment_name=environment_name
                )
                output._console.print(
                    f"Updated ({environment_name}) {key} -> {new_value}"
                )


def environment_information(
    project: Project,
    output: OutputManager,
    environment_name: str = None,
):

    _environment_name = environment_name or project.get_current_environment_name()

    environment_info = project.get_environment_settings_info(_environment_name)

    output._console.print(f"{_environment_name}:")

    for key, val in environment_info.dict().items():
        output._console.print(f"    {key} -> {val}")
