"""Utilities for running custom scripts

"""
from typing import List

from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager


def execute_run_cli(args) -> None:
    ws = Workspace.instance()

    output_manager = OutputManager()

    run_command(ws, output_manager, args)


def run_command(
    subcommand: str,
    subcommand_args: List[str],
    workspace: Workspace,
    output: OutputManager,
) -> None:
    """Attempts to find and run a user defined command.

    format:
    cdev run <sub_command> <args>

    Args:
        workspace (Workspace): Workspace to execute the process within.
        output (OutputManager): Output manager for sending messages to the console.
        cli_args (Namespace): Arguments for the command.
    """
    workspace.execute_command(subcommand, subcommand_args, output=output)
