"""Utilities for creating a new resource state

"""

from ..constructs.workspace import Workspace


def create_resource_state_cli(args) -> None:

    WORKSPACE = Workspace.instance()

    create_resource_state(WORKSPACE)


def create_resource_state(workspace: Workspace) -> None:
    new_uuid = workspace.get_backend().create_resource_state("demo")
