#!/usr/bin/env python
import argparse
from ast import parse
import os

from  .. import commands as commands

from . import output


parser = argparse.ArgumentParser(description='cdev cli')
subparsers = parser.add_subparsers(title='sub_command', description='valid subcommands')


CDEV_COMMANDS = [
    {
        "name": "plan",
        "help": "See the differences that have been made since the last deployment",
        "default": commands.plan
    }, 
    
    {
        "name": "deploy",
        "help": "Deploy a set of changes",
        "default": commands.deploy
    }, 
    
    {
        "name": "init",
        "help": "Create a new project",
        "default": commands.init
    },
    {
        "name": "environment",
        "help": "Change and create environments for deployment",
        "default": commands.environment,
        "subcommands": [
            {
                "command": "ls",
                "help": "Show all available environments",
                "args": [
                    {"dest": "--all", "help": "show more details", "action":"store_true"}
                ]
            },
            {
                "command": "set",
                "help": "Set the current working environment",
                "args": [
                    {"dest": "env", "type": str, "help": "environment you want set as the new working environment"}
                ]
            },
            {
                "command": "get",
                "help": "Get information about an environment",
                "args": [
                    {"dest": "env", "type": str, "help": "environment you want info about"}
                ]
            },
            {
                "command": "create",
                "help": "Create a new environment",
                "args": [
                    {"dest": "env", "type": str, "help": "name of environment you want to create"}
                ]
            }
        ]
    },
    {
        "name": "user",
        "help": "Change and create user information",
        "default": commands.user,
        "subcommands": [
            {
                "command": "ls",
                "help": "Show available users",
                "args": [
                    {"dest": "--all", "help": "show more details", "action":"store_true"}
                ]
            },
            {
                "command": "set",
                "help": "",
                "args": []
            },
            {
                "command": "get",
                "help": "",
                "args": []
            },
            {
                "command": "create",
                "help": "",
                "args": []
            }
        ]
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
        tmp.set_defaults(func=command.get("default"))
        tmp.add_argument("--output", type=str, choices=["json", "plain-text", "rich"],
                                help="change the type of output generated")



args = parser.parse_args()
args.func(args)

