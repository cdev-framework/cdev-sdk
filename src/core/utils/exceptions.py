"""Base Exceptions to use within the framework

These are the two exceptions that are expected to be used at the module level throughout Cdev. Within a module, it should have its own more precise
exceptions, but they should be wrapped in these classes before being exposed at the module level. Any other error that is raised will be treated as 
an uncaught exception and not the responsibility of other modules. 

Warning: Something is not correct but the process can continue running.
Error: Something has reached a state that should terminate the process. 

"""
import sys


class Cdev_Warning(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
        super().__init__(self.msg)


class Cdev_Error(Exception):
    def __init__(self, msg: str, nested_exceptions: Exception=None) -> None:
        self.msg = msg
        self.nested_exceptions = nested_exceptions
        super().__init__(self.msg)


def end_process():
    sys.exit(1)
