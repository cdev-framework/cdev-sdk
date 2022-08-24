"""Utilities for initializing the workspace

"""


import os

from core.constructs.workspace import (
    Workspace_Info,
    load_workspace,
    initialize_workspace,
)
from core.default.workspace import local_workspace_manager


def initialize_workspace_cli(args) -> None:

    workspace_manager = local_workspace_manager(os.getcwd())
    workspace_config = workspace_manager.load_workspace_configuration()
    initialize_workspace_command(workspace_config)


def initialize_workspace_command(workspace_config: Workspace_Info) -> None:

    ws = load_workspace(workspace_config)

    initialize_workspace(ws, workspace_config)
