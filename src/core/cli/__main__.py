#!/usr/bin/env python
import argparse
from ast import parse
from typing import Callable, Any

from ..commands import create_workspace, initialize_workspace, run, execute_frontend, create_resource_state
from ..constructs.workspace import Workspace

parser = argparse.ArgumentParser(description='cdev cli')
subparsers = parser.add_subparsers(title='sub_command', description='valid subcommands')


def wrap_initialize_workspace(command: Callable) -> Callable[[Any], Any]:

    def wrapped_caller(args):
        try:
            
            initialize_workspace.initialize_workspace_cli(args)
        except Exception as e:
            print(f"Could not initialize the workspace to call {command}")
            print(e)
            return

        command(args)


    return wrapped_caller


CDEV_COMMANDS = [
    {
        "name": "init",
        "help": "Create a new instance of a workspace",
        "default": create_workspace.create_workspace
    },
    {
        "name": "plan",
        "help": "Create a new instance of a workspace",
        "default": wrap_initialize_workspace(execute_frontend.execute_frontend_cli),
        "args": [
           
        ]
    },
    {
        "name": "create_resource_state",
        "help": "Create a new resource state",
        "default": wrap_initialize_workspace(create_resource_state.create_resource_state_cli),
        "args": [
           
        ]
    }, 
    {
        "name": "run",
        "help": "This command is used to run user defined and resource functions.",
        "default": wrap_initialize_workspace(run.run_command),
        "args": [
            {"dest": "subcommand", "help": "the user defined command to call"},
            {"dest": "args", "nargs": argparse.REMAINDER}
        ]
    },
    
]





def subcommand_function_wrapper(name, subcommand):
    # This wraps a function so that is can be used for subcommands by basing the subcommand as the first arg to the function 
    # then the remaining args as the second arg
    def inner(args):

        return command(subcommand, args)

    return inner

for command in CDEV_COMMANDS:
    tmp = subparsers.add_parser(command.get("name"), help=command.get("help"))
    

    if command.get("subcommands"):
        tmp.set_defaults(func=subcommand_function_wrapper("", command.get("default")))
        t1 = tmp.add_subparsers()

        for subcommand in command.get("subcommands"):
            t2 = t1.add_parser(subcommand.get("command"), help=subcommand.get("help"))
            t2.set_defaults(func=subcommand_function_wrapper(subcommand.get("command"), command.get("default")))

            for arg in subcommand.get("args"):
                dest = arg.get("dest")
                arg.pop("dest")
                t2.add_argument(dest, **arg)


            t2.add_argument("--output", type=str, choices=["json", "plain-text", "rich"],
                                help="change the type of output generated")

    else:
        if command.get("args"):
            for arg in command.get("args"):
                dest = arg.get("dest")
                arg.pop("dest")
                tmp.add_argument(dest, **arg)
                

        
        tmp.set_defaults(func=command.get("default"))
        

        

        tmp.add_argument("--output", type=str, choices=["json", "plain-text", "rich"],
                                help="change the type of output generated")



args = parser.parse_args()
args.func(args)

