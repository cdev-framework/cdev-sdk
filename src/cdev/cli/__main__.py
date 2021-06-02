#!/usr/bin/env python
import argparse
import os

import cdev.frontend.commands as commands

from . import output

parser = argparse.ArgumentParser(description='cdev cli')

CDEV_COMMANDS = ["plan", "build", "form", "init"]
parser.add_argument('command', metavar="<command>", type=str, choices=CDEV_COMMANDS)


args = parser.parse_args()

if args.command == "plan":
    output.print_local_diffs(commands.plan())
elif args.command == "form":
    print("YOU CALLED FORM")
elif args.command == "init":
    commands.init()

