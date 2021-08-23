#!/usr/bin/env python
import argparse
import os
import logging.config

from  .. import commands as commands

from . import output

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), "logging.ini"), disable_existing_loggers=False)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='cdev cli')

CDEV_COMMANDS = ["plan", "deploy" , "init"]
parser.add_argument('command', metavar="<command>", type=str, choices=CDEV_COMMANDS)



args = parser.parse_args()

if args.command == "plan":
    logger.info("CALLING PLAN COMMAND")
    commands.plan()
elif args.command == "deploy":
    commands.deploy()
elif args.command == "init":
    commands.init()

