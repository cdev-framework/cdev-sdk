"""Utilities for creating a new resource state

"""

from ..constructs.workspace import Workspace


def create_resource_state_cli(args) -> None:

    workspace = Workspace.instance()
    create_resource_state(workspace)


def create_resource_state(workspace: Workspace) -> None:
    workspace.get_backend().create_resource_state("demo")
