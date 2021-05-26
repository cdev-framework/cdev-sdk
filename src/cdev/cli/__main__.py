#!/usr/bin/env python
import argparse
import os

import cdev.fs_manager.finder as fs
import cdev.fs_manager.writer as file_writer


parser = argparse.ArgumentParser(description='cdev cli')

CDEV_COMMANDS = ["plan", "build", "form"]
parser.add_argument('command', metavar="<command>", type=str, choices=CDEV_COMMANDS)

args = parser.parse_args()

if args.command == "plan":
    print("YOU CALLED PLAN")
    fs.parse_folder(os.path.join(".", "src"))
    
elif args.command == "form":
    print("YOU CALLED FORM")
