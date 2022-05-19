from rich.prompt import Confirm
from typing import List, Tuple, Any

from cdev.constructs.project import Project
from cdev.cli.logger import set_global_logger_from_cli


def environment_cli(args: List[Any]) -> None:
    command = args[0]
    parsed_args = vars(args[1])
    
    set_global_logger_from_cli(parsed_args.get("loglevel"))

    if command == "":
        # ANIBAL is this sub-command or command name?
        print(
            "You must provide a sub-command. run `cdev environment --help` for more information on available subcommands"
        )
    elif command == "ls":
        list_environments()
    elif command == "get":
        pass
    elif command == "set":
        set_current_environment(parsed_args.get("env"))
    elif command == "create":
        create_environment(parsed_args.get("env"))
    elif command == "settings_information":
        settings_information(parsed_args.get('key'), parsed_args.get('new_value'), parsed_args.get('all'))


def list_environments() -> None:
    """
    Get the current list of environments and the current environment from the Project object.
    Must be called when the Project is in the UNINITIALIZED phase.
    """
    my_project = Project.instance()

    current_environment_name = my_project.get_current_environment_name()
    all_environment_names = my_project.get_all_environment_names()

    for environment_name in all_environment_names:
        if current_environment_name == environment_name:
            print(f"> {environment_name}")
        else:
            print(environment_name)


def set_current_environment(new_current_environment: str) -> None:

    try:
        my_project = Project.instance()
        my_project.set_current_environment(new_current_environment)
        print(f"Set Current Environment -> {new_current_environment}")
        # ANIBAL we should use specific Exceptions to provide better feedback
    except Exception as e:
        print(f'Could not set {new_current_environment} as the environment')


def create_environment(new_environment_name: str) -> None:
    my_project = Project.instance()

    # ANIBAL: We should check if the environment name already exists
    # Also sanitize it
    my_project.create_environment(new_environment_name)

    print(f"Created Environment -> {new_environment_name}")


def settings_information(key: str = None, new_value: str = None, all: bool = False) -> None:

    if all and not new_value:
        raise Exception('Must use --all with --new-value')

    if not new_value:
        my_project = Project.instance()
        settings_info = my_project.get_settings_info()
        settings_dict = settings_info.dict()
        print(f'Settings info for Environment {my_project.get_current_environment_name()}:')
        if key:
            #Print desired key
            if key not in settings_dict:
                raise Exception(f"Key {key} not in settings information {settings_info}")

            print(f"    {key} -> {settings_dict.get(key)}")
        else:
            # Print all values
            for key, value in settings_dict.items():
                print(f"    {key} -> {value}")
    else:
        if not key:
            raise Exception('Must use --new-value with --key')

        my_project = Project.instance()
        if not all:
            settings_info = my_project.get_settings_info()

            # ANIBAL: We don't check the result?
            Confirm.ask(f"Are you sure you want to update {key} to {new_value} for the current environment ({my_project.get_current_environment_name()})?")

            setattr(settings_info, key, new_value)

            my_project.update_settings_info(settings_info)
            print(f"Updated {key} -> {new_value}")
        else:
            # ANIBAL: We don't check the result?
            Confirm.ask(f"Are you sure you want to update {key} to {new_value} for all environments?")
            for environment_name in my_project.get_all_environment_names():
                settings_info = my_project.get_settings_info(environment_name)

                setattr(settings_info, key, new_value)

                my_project.update_settings_info(settings_info, environment_name)
                print(f"Updated ({environment_name}) {key} -> {new_value}")

    

