"""Utilities for running custom scripts 

"""


from ..constructs.commands import BaseCommand, BaseCommandContainer
from ..constructs.workspace import Workspace
from ..constructs.output_manager import OutputManager


def execute_run_cli(args):
    ws = Workspace.instance()
    
    output_manager = OutputManager()

    run_command(ws, output_manager, args)


def run_command(workspace: Workspace, output: OutputManager, cli_args):
    """
    Attempts to find and run a user defined command

    format:
    cdev run <sub_command> <args>
    """
    # Convert namespace into dict
    params = vars(cli_args)

    # This is the command to run... It can be a single command or a path to the command where the path is '.' delimitated
    sub_command = params.get("subcommand")
    command_args = params.get("args") if params.get("args") else []

    
    try:
        workspace.execute_command(sub_command, command_args)
    except Exception as e:
        print(e)
        return
