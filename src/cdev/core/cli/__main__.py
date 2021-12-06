#!/usr/bin/env python
import argparse
from ast import parse
import os

from cdev.core.commands import initialize_workspace

parser = argparse.ArgumentParser(description='cdev cli')
subparsers = parser.add_subparsers(title='sub_command', description='valid subcommands')

def myfunc():
    print("From cdev core")

CDEV_COMMANDS = [
    {
        "name": "exec",
        "help": "See the differences that have been made since the last deployment",
        "default": myfunc
    }, 
    {
        "name": "init",
        "help": "Create a new instance of a workspace and connect it to a backend",
        "default": initialize_workspace.initialize_workspace
    }, 
    
]



def subcommand_function_wrapper(name, func):
    # This wraps a function so that is can be used for subcommands by basing the subcommand as the first arg to the function 
    # then the remaining args as the second arg
    def inner(args):

        return func(name, args)

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

