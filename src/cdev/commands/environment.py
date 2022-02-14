from typing import List, Tuple

from cdev.constructs.project import Project
from cdev.cli.logger import set_global_logger_from_cli


def environment_cli(args):
    command = args[0]
    parsed_args = vars(args[1])
    
    set_global_logger_from_cli(parsed_args.get("loglevel"))


    if command == "":
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


def list_environments() -> Tuple[List[str], str]:
    """
    Get the current list of environments and the current environment from the Project object.
    Must be called when the Project is in the UNINITIALIZED phase.
    """

    myProject = Project.instance()

    current_environment_name = myProject.get_current_environment_name()
    all_environment_names = myProject.get_all_environment_names()

    for environment_name in all_environment_names:
        if current_environment_name == environment_name:
            print(f"> {environment_name}")

        else:
            print(environment_name)


def set_current_environment(new_current_environment: str):
    myProject = Project.instance()

    try:
        myProject.set_current_environment(new_current_environment)
    except Exception as e:
        print(f'Could not set {new_current_environment} as the environment')
        return

    print(f"Set Current Environment -> {new_current_environment}")


def create_environment(new_environment_name: str):
    myProject = Project.instance()

    myProject.create_environment(new_environment_name)

    print(f"Created Environment -> {new_environment_name}")
