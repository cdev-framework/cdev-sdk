#!/usr/bin/env python
import argparse
import os

from  .. import commands as commands

from . import output

parser = argparse.ArgumentParser(description='cdev cli')

CDEV_COMMANDS = ["plan", "deploy" , "init"]
parser.add_argument('command', metavar="<command>", type=str, choices=CDEV_COMMANDS)


args = parser.parse_args()

if args.command == "plan":
    commands.plan()
elif args.command == "deploy":
    commands.deploy()
elif args.command == "init":
    commands.init()

