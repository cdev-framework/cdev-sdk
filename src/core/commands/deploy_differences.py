"""Utilities for creating a deploying a set of changes

"""
from typing import Optional

from core.constructs.output_manager import OutputManager
from core.constructs.workspace import Workspace, Workspace_State
from rich.prompt import Confirm
from .execute_frontend import execute_frontend


def execute_deployment_cli(args) -> None:

    workspace = Workspace.instance()
    execute_deployment(workspace, OutputManager())


def execute_deployment(
    workspace: Workspace, output: OutputManager, no_prompt: Optional[bool] = False
) -> None:
    """Execute the process for a deployment. This includes generating the current frontend representation of the desired resources.
    Then after confirmation, deploy any needed changes.

    Args:
        workspace (Workspace): Workspace to execute the process within.
        output (OutputManager): Output manager for sending messages to the console.
        no_prompt (bool): If set to True, we don't ask the user to confirm before deploying the resources.
    """
    unsorted_differences = execute_frontend(workspace, output)

    if not unsorted_differences:
        return

    differences_structured = workspace.sort_differences(unsorted_differences)

    if not no_prompt:
        print("")
        do_deployment = Confirm.ask("Do you want to deploy differences?")

        if not do_deployment:
            return

    workspace.set_state(Workspace_State.EXECUTING_BACKEND)
    workspace.deploy_differences(differences_structured)

    for tag, cloud_output in workspace.render_outputs():
        print(f"{tag} -> {cloud_output}")
