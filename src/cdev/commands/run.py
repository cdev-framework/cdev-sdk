import os
from typing import List

def run_command(args):
    print(args)
    params = vars(args)

    sub_command = params.get("args")[0]


    if len(sub_command.split(".")) > 0:
        print("nested command")

        nested_command = sub_command.split(".")
        print(nested_command)


def _find_command(command: List[str]) -> str:
    """
    This command will search for the given command. Search order is:
    
    1. default included cdev resources
    2. Installed applications
    3. local project commands
    """
    pass
