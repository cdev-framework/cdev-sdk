from typing import List, Tuple

from cdev.constructs.project import Project
from cdev.cli.logger import set_global_logger_from_cli


def environment_cli(args):
    config = args[0]
    set_global_logger_from_cli(config.loglevel)

    command = args[0]
    parsed_args = vars(args[1])

    if command == "":
        print(
            "You must provide a sub-command. run `cdev environment --help` for more information on available subcommands"
        )
    elif command == "ls":
        print(list_environments())
    elif command == "get":
        pass
    elif command == "set":
        set_current_environment(parsed_args.get("env"))
    elif command == "create":

        print(parsed_args)
        create_environment(parsed_args.get("env"))


def list_environments() -> Tuple[List[str], str]:
    """
    Get the current list of environments and the current environment from the Project object.
    Must be called when the Project is in the UNINITIALIZED phase.
    """

    myProject = Project.instance()

    return (
        myProject.get_all_environment_names(),
        myProject.get_current_environment_name(),
    )


def set_current_environment(new_current_environment: str):
    print(new_current_environment)
    myProject = Project.instance()

    myProject.set_current_environment(new_current_environment)


def create_environment(new_environment_name: str):
    print(new_environment_name)
    myProject = Project.instance()

    myProject.create_environment(new_environment_name)
