"""Base Exceptions to use within the framework

These are the two exceptions that are expected to be used at the module level throughout Cdev. Within a module, it should have its own more precise
exceptions, but they should be wrapped in these classes before being exposed at the module level. Any other error that is raised will be treated as
an uncaught exception and not the responsibility of other modules.

Warning: Something is not correct but the process can continue running.
Error: Something has reached a state that should terminate the process.

"""
import sys
from dataclasses import dataclass, field

from typing import List


@dataclass
class cdev_core_error(Exception):
    error_message: str
    help_message: str
    help_resources: List[str]


def end_process():
    sys.exit(1)
