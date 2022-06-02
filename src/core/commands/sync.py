"""Utilities for running custom scripts

"""
from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager
from core.constructs.workspace_watcher import WorkspaceWatcher


def execute_sync(args) -> None:
    ws = Workspace.instance()

    output_manager = OutputManager()

    core_sync_command(ws, output_manager, args)


def core_sync_command(workspace: Workspace, output: OutputManager, cli_args) -> None:
    """
    Attempts to find and run a user defined command

    format:
    cdev sync <sub_command> <args>
    """
    # Convert namespace into dict
    try:
        workspace_watcher = WorkspaceWatcher(workspace, output)
        workspace_watcher.watch()
    except Exception as e:
        print(e)
        return
