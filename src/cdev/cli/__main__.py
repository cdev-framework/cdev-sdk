import argparse
from ast import parse
import logging
import traceback
from typing import Callable, Any

from ..commands import initializer, environment, plan, deploy, run, cloud_output, local_development, destroy

parser = argparse.ArgumentParser(description="cdev cli")
subparsers = parser.add_subparsers(title="sub_command", description="valid subcommands")

def wrap_load_project(command: Callable) -> Callable[[Any], Any]:
    def wrapped_caller(*args, **kwargs):
        try:
            initializer.load_project(args)
        except Exception as e:
            print(f"Could not load the project to call {command}")
            print(e)
            print(traceback.format_exc())

            return

        command(args)

    return wrapped_caller


def wrap_load_and_initialize_project(command: Callable) -> Callable[[Any], Any]:
    def wrapped_caller(*args, **kwargs):
        try:
            initializer.load_and_initialize_project(args)
        except Exception as e:
            print(f"Could not load and initialize the project to call {command}")
            print(e)
            print(traceback.format_exc())
            return

        command(args)

    return wrapped_caller


CDEV_COMMANDS = [
    {
        "name": "plan",
        "help": "See the differences that have been made since the last deployment",
        "default": wrap_load_and_initialize_project(plan.plan_command_cli),
    },
    {
        "name": "init",
        "help": "Create a new project",
        "default": initializer.create_project_cli,
        "args": [
            {"dest": "name", "type": str, "help": "Name of the new project"},
            {"dest": "--template", "type": str, "help": "Name of the template for the new project"}
        ],
    },
    {
        "name": "develop",
        "help": "Open an interactive development environment",
        "default": wrap_load_and_initialize_project(local_development.develop_command_cli),
        "args": [
            {"dest": "--complex", "help": "run a simple follower instead of full development environment", "action":"store_true"}
        ]
    },
    {
        "name": "destroy",
        "help": "Destroy all the resources in the current environment",
        "default": wrap_load_and_initialize_project(destroy.destroy_command_cli)
    }, 

    {
        "name": "output",
        "help": "See the generated cloud output",
        "default": wrap_load_and_initialize_project(cloud_output.cloud_output_command_cli),
        "args": [
            {"dest": "cloud_output_id", "type": str, "help": "Id of the cloud output to display. ex: <component>.<ruuid>.<cdev_name>.<output_key>"},
            {"dest": "--value", "help": "display only the value. Helpful for exporting values.", "action":"store_true"}
        ]
    }, 
    {
        "name": "environment",
        "help": "Change and create environments for deployment",
        "default": wrap_load_and_initialize_project(environment.environment_cli),
        "subcommands": [
            {
                "command": "ls",
                "help": "Show all available environments",
                "args": [
                    {
                        "dest": "--all",
                        "help": "show more details",
                        "action": "store_true",
                    }
                ],
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
                "command": "get",
                "help": "Get information about an environment",
                "args": [
                    {
                        "dest": "env",
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
                    }
                ],
            },
        ],
    },
    {
        "name": "deploy",
        "help": "Deploy a set of changes",
        "default": wrap_load_and_initialize_project(deploy.deploy_command_cli)
    },
    {
        "name": "run",
        "help": "This command is used to run user defined and resource functions.",
        "default": wrap_load_and_initialize_project(run.run_command_cli),
        "args": [
            {"dest": "subcommand", "help": "the user defined command to call"},
            {"dest": "args", "nargs": argparse.REMAINDER},
        ],
    },
]


def subcommand_function_wrapper(name, func):
    # This wraps a function so that is can be used for subcommands by basing the subcommand as the first arg to the function
    # then the remaining args as the second arg
    def inner(args):

        return func(name, args)

    return inner


def add_general_output_options(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--output",
        type=str,
        choices=["json", "plain-text", "rich"],
        help="change the type of output generated",
    )

    parser.add_argument(
        '-d', '--debug',
        help="Print debug log statements. This is mostly for development use",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )

    parser.add_argument(
        '-v', '--verbose',
        help="Print info log message. Use this to get a more detailed understanding of what is executing.",
        action="store_const", dest="loglevel", const=logging.INFO,
    )


for command in CDEV_COMMANDS:
    tmp = subparsers.add_parser(command.get("name"), help=command.get("help"))

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

            for arg in subcommand.get("args"):
                dest = arg.get("dest")
                arg.pop("dest")
                t2.add_argument(dest, **arg)

           
            add_general_output_options(t2)

    else:
        if command.get("args"):
            for arg in command.get("args"):
                dest = arg.get("dest")
                arg.pop("dest")
                tmp.add_argument(dest, **arg)

        tmp.set_defaults(func=command.get("default"))

        add_general_output_options(tmp)


args = parser.parse_args()
args.func(args)