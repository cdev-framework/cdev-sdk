"""Utilities for creating a deploying a set of changes 

"""

from core.constructs.output_manager import OutputManager
from ..constructs.workspace import Workspace, Workspace_State
from rich.prompt import Confirm
from .execute_frontend import execute_frontend

import networkx as nx


def execute_deployment_cli(args):

    workspace = Workspace.instance()
    execute_deployment(workspace, OutputManager())


def execute_deployment(workspace: Workspace, output: OutputManager):
    unsorted_differences = execute_frontend(workspace, output)

    if not unsorted_differences:
        return

    differences_structured = workspace.sort_differences(unsorted_differences)

    print("")
    do_deployment = Confirm.ask("Do you want to deploy differences?")

    if do_deployment is not True:
        return

    workspace.set_state(Workspace_State.EXECUTING_BACKEND)
    workspace.deploy_differences(differences_structured)

    for tag, cloud_output in workspace.render_outputs():
        print(f"{tag} -> {cloud_output}")
