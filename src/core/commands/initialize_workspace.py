"""Utilities for initializing the workspace

"""


import os

from ..constructs.workspace import Workspace_Info

from ..constructs.workspace import load_and_initialize_workspace
from ..default.workspace import local_workspace_manager


def initialize_workspace_cli(args):

    workspace_manager = local_workspace_manager(os.getcwd())
    workspace_config = workspace_manager.load_workspace_configuration()
    initialize_workspace(workspace_config)


def initialize_workspace(workspace_config: Workspace_Info):

    load_and_initialize_workspace(workspace_config)
