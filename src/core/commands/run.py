"""Utilities for running custom scripts

"""


from argparse import Namespace
from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager


def execute_run_cli(args) -> None:
    ws = Workspace.instance()

    output_manager = OutputManager()

    run_command(ws, output_manager, args)


def run_command(
    workspace: Workspace, output: OutputManager, cli_args: Namespace
) -> None:
    """Attempts to find and run a user defined command.

    format:
    cdev run <sub_command> <args>

    Args:
        workspace (Workspace): Workspace to execute the process within.
        output (OutputManager): Output manager for sending messages to the console.
        cli_args (Namespace): Arguments for the command.
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
