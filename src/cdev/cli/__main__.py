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
    rv = fs.find_serverless_function_information_from_file(os.path.join(".", "main.py"))
    print(rv)
    file_writer.write_intermediate_files(os.path.join(".", "main.py"), rv)
elif args.command == "form":
    print("YOU CALLED FORM")
