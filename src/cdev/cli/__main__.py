import argparse
from dataclasses import dataclass, field
import json
import logging
import os
from typing import Any, Callable, List

from pydantic import FilePath, ValidationError

from core.constructs.output_manager import OutputManager
from core.utils.exceptions import cdev_core_error, wrap_base_exception

from ..commands import (
    cloud_output,
    environment,
    plan,
    deploy,
    destroy,
    project_initializer,
    run,
    sync,
    git_safe,
)

from cdev.constructs.project import CDEV_PROJECT_FILE, CDEV_FOLDER, Project
from cdev.default.project import local_project, local_project_info

parser = argparse.ArgumentParser(description="cdev cli")
subparsers = parser.add_subparsers(title="sub_command", description="valid subcommands")

LOG_LEVEL_ARG = "loglevel"
OUTPUT_TYPE_ARG = "output_type"


###############################
##### Exceptions
###############################


@dataclass
class ProjectInfoError(cdev_core_error):
    help_message: str = (
        "   The project info files will most likely need to be fixed by hand."
    )
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ProjectInfoJsonDecoding(cdev_core_error):
    help_message: str = "   The project info files will most likely need to be fixed by hand. The File should be a valid Json."
    help_resources: List[str] = field(default_factory=lambda: [])


###############################
##### API
###############################


def wrap_load_and_initialize_project(
    command: Callable, initialize: bool = True
) -> Callable[[Any], Any]:
    """Helper annotation that makes sure that the global Project object is in the correct state before running a given command.

    Args:
        command (Callable): command to run
        initialize (bool, optional): Initialize the Project. Defaults to True.

    Returns:
        Callable[[Any], Any]: Wrapped function
    """

    def wrapped_caller(*args, **kwargs):
        if len(args) == 1:
            dict_args = vars(args[0])

        elif len(args) == 2:
            dict_args = vars(args[1])

        else:
            return

        log_level = dict_args.pop(LOG_LEVEL_ARG)
        output_type = dict_args.pop(OUTPUT_TYPE_ARG)

        _output_manager = _initialize_output_manager(output_type=output_type)

        try:
            _project = load_and_initialize_project(initialize=initialize)
        except cdev_core_error as e:
            _output_manager.print_exception(e)
            return
        except Exception as e:
            _output_manager.print_exception(wrap_base_exception(e))
            return

        try:
            if len(args) == 1:
                command(
                    **dict_args,
                    loglevel=log_level,
                    output_manager=_output_manager,
                    project=_project,
                )
            else:
                command(
                    args[0],
                    args[1],
                    loglevel=log_level,
                    output_manager=_output_manager,
                    project=_project,
                )
        except cdev_core_error as e:
            _output_manager.print_exception(e)
        except Exception as e:
            _output_manager.print_exception(wrap_base_exception(e))

    return wrapped_caller


def _initialize_output_manager(output_type: str) -> OutputManager:
    return OutputManager()


def load_and_initialize_project(initialize: bool = True) -> Project:
    """Create the global instance of the `Project` object as a `local_project` instance. If provided, also initialize the `Project`.

    Args:
        initialize (bool, optional): Initialize the project. Defaults to True.
    """
    base_directory = os.getcwd()

    project_info_location = os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)
    project_info = _load_local_project_information(project_info_location)

    project = local_project(
        project_info=project_info, project_info_filepath=project_info_location
    )
    if initialize:
        project.initialize_project()

    return project


def _load_local_project_information(
    project_info_location: FilePath,
) -> local_project_info:
    """Help function to load the project info json file

    Args:
        project_info_location (FilePath): location of project info json

    Returns:
        local_project_info
    """
    with open(project_info_location, "r") as fh:
        try:
            json_information = json.load(fh)

            local_project_info_model = local_project_info(**json_information)

        except ValidationError as e:
            raise ProjectInfoError(
                error_message=f"Could not convert loaded json data from {project_info_location} into a valid 'local_project_info' object because of pydantic validation error"
            )

        except json.JSONDecodeError as e:
            raise ProjectInfoJsonDecoding(
                error_message=f"Could not load project info from {project_info_location} as json data"
            )

    return local_project_info_model


CDEV_COMMANDS = [
    {
        "name": "init",
        "help": "Create a new project",
        "default": project_initializer.create_project_cli,
        "args": [
            {"dest": "name", "type": str, "help": "Name of the new project"},
            {
                "dest": "--template",
                "type": str,
                "default": "quick-start",
                "help": "Name of the template for the new project. Defaults to 'quick-start'.",
            },
        ],
    },
    {
        "name": "environment",
        "help": "Change and create environments for deployment",
        "default": wrap_load_and_initialize_project(
            environment.environment_cli, initialize=False
        ),
        "subcommands": [
            {
                "command": "ls",
                "help": "Show all available environments",
            },
            {
                "command": "set",
                "help": "Set the current working environment",
                "args": [
                    {
                        "dest": "env",
                        "type": str,
                        "help": "environment you want set as the new working environment",
                    }
                ],
            },
            {
                "command": "info",
                "help": "Get information about an environment",
                "args": [
                    {
                        "dest": "--env",
                        "type": str,
                        "help": "environment you want info about",
                    }
                ],
            },
            {
                "command": "create",
                "help": "Create a new environment",
                "args": [
                    {
                        "dest": "env",
                        "type": str,
                        "help": "name of environment you want to create",
                    }
                ],
            },
            {
                "command": "settings_information",
                "help": "Get or Set information about the settings of an environment",
                "args": [
                    {
                        "dest": "--key",
                        "type": str,
                        "help": "The key to get or set.",
                    },
                    {
                        "dest": "--new-value",
                        "type": str,
                        "help": "New value of the variable. Must be used with --key.",
                    },
                    {
                        "dest": "--all",
                        "action": "store_true",
                        "help": "Set the value for all environments. Must be used with --new-value.",
                    },
                ],
            },
        ],
    },
    {
        "name": "plan",
        "help": "See the differences that have been made since the last deployment",
        "default": wrap_load_and_initialize_project(plan.plan_command_cli),
    },
    {
        "name": "deploy",
        "help": "Deploy a set of changes",
        "default": wrap_load_and_initialize_project(deploy.deploy_command_cli),
        "args": [
            {
                "dest": "--disable-prompt",
                "action": "store_true",
                "help": "by default we ask for confirmation before deploying the resources. Turn this on and perform deployments w/o requiring confirmation",
            },
        ],
    },
    {
        "name": "destroy",
        "help": "Destroy all the resources in the current environment",
        "default": wrap_load_and_initialize_project(destroy.destroy_command_cli),
    },
    {
        "name": "output",
        "help": "See the generated cloud output",
        "default": wrap_load_and_initialize_project(
            cloud_output.cloud_output_command_cli
        ),
        "args": [
            {
                "dest": "cloud_output_id",
                "type": str,
                "help": "Id of the cloud output to display. ex: <component>.<ruuid>.<cdev_name>.<output_key>",
            },
            {
                "dest": "--value",
                "help": "display only the value. Helpful for exporting values.",
                "action": "store_true",
            },
        ],
    },
    {
        "name": "run",
        "help": "This command is used to run user defined and resource functions.",
        "default": wrap_load_and_initialize_project(run.run_command_cli),
        "args": [
            {"dest": "subcommand", "help": "the user defined command to call"},
            {"dest": "subcommand_args", "nargs": argparse.REMAINDER},
        ],
    },
    {
        "name": "sync",
        "help": "Watch for changes in the filesystem and perform a deploy automatically",
        "default": wrap_load_and_initialize_project(sync.sync_command_cli),
        "args": [
            {
                "dest": "--no-default",
                "action": "store_true",
                "help": "by default we ignore certain files and watch for some of them. If you want complete control on what is considered a change, turn this on and set your custom filters using --watch and --ignore",
            },
            {
                "dest": "--disable-prompt",
                "action": "store_true",
                "help": "by default we ask for confirmation before deploying changes. Turn this on and perform deployments w/o requiring confirmation",
            },
            {
                "dest": "--watch",
                "type": str,
                "help": "watch any file that matches the following pattern ['src/**/*.py','settings/*']",
            },
            {
                "dest": "--ignore",
                "type": str,
                "help": "do not watch for any file that matches the following pattern ['.cdev/**','__pycache__/*']",
            },
        ],
    },
    {
        "name": "git-safe",
        "help": "Safe versions of some git operations",
        "default": git_safe.git_safe_cli,
        "subcommands": [
            {
                "command": "install-merger",
                "help": "Install the cdev custom git merger to help properly merge the underlying used by Cdev.",
            },
            {
                "command": "project-merger",
                "help": "CLI interface to the custom merger",
                "args": [
                    {
                        "dest": "current_fp",
                        "type": str,
                        "help": "Tmp file that contains the current version of the file",
                    },
                    {
                        "dest": "other_fp",
                        "type": str,
                        "help": "tmp file that contains the other commits version of the file",
                    },
                ],
            },
            {
                "command": "merge",
                "help": "Safely run `git merge`",
                "args": [
                    {
                        "dest": "commit",
                        "type": str,
                        "help": "Commits, usually other branch heads, to merge into our branch.",
                        "nargs": "?",
                        "default": None,
                    },
                    {
                        "dest": "--abort",
                        "action": "store_true",
                        "help": "Commits, usually other branch heads, to merge into our branch.",
                    },
                    {
                        "dest": "--continue",
                        "action": "store_true",
                        "help": "Commits, usually other branch heads, to merge into our branch.",
                    },
                    {
                        "dest": "--quit",
                        "action": "store_true",
                        "help": "Commits, usually other branch heads, to merge into our branch.",
                    },
                ],
            },
            {
                "command": "pull",
                "help": "Safely run `git pull`",
                "args": [
                    {
                        "dest": "repository",
                        "type": str,
                        "help": "Repository",
                        "default": None,
                        "nargs": "?",
                    },
                    {
                        "dest": "ref_spec",
                        "type": str,
                        "help": "commit like object",
                        "default": None,
                        "nargs": "?",
                    },
                ],
            },
        ],
    },
]


def subcommand_function_wrapper(name, func):
    # This wraps a function so that is can be used for subcommands by basing the subcommand as the first arg to the function
    # then the remaining args as the second arg
    def inner(args):

        return func(name, args)

    return inner


def add_general_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "plain-text", "rich"],
        dest=OUTPUT_TYPE_ARG,
        default="rich",
        help="BASE CDEV OPTION -> change the type of output generated",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="BASE CDEV OPTION -> Print info log message. Use this to get a more detailed understanding of what is executing.",
        action="store_const",
        dest=LOG_LEVEL_ARG,
        const=logging.INFO,
    )


for command in CDEV_COMMANDS:
    tmp = subparsers.add_parser(command.get("name"), help=command.get("help"))
    add_general_output_options(tmp)

    if command.get("subcommands"):
        tmp.set_defaults(func=subcommand_function_wrapper("", command.get("default")))
        t1 = tmp.add_subparsers()

        for subcommand in command.get("subcommands"):
            t2 = t1.add_parser(subcommand.get("command"), help=subcommand.get("help"))
            t2.set_defaults(
                func=subcommand_function_wrapper(
                    subcommand.get("command"), command.get("default")
                )
            )

            for arg in subcommand.get("args", []):
                dest = arg.get("dest")
                arg.pop("dest")
                t2.add_argument(dest, **arg)

            add_general_output_options(t2)

    else:
        if command.get("args"):
            for arg in command.get("args"):
                dest = arg.pop("dest")
                tmp.add_argument(dest, **arg)

        tmp.set_defaults(func=command.get("default"))


args = parser.parse_args()
args.func(args)
