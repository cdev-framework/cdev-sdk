from ..constructs.workspace import Workspace, Workspace_State
from rich.prompt import Confirm
from .execute_frontend import execute_frontend

import networkx as nx


def execute_deployment_cli(args):

    WORKSPACE = Workspace.instance()

    execute_deployment(WORKSPACE)



def execute_deployment(workspace: Workspace):
    differences = execute_frontend(workspace)

   
    do_deployment = Confirm.ask("Do you want to deploy differences?")

    if not do_deployment:
        return

    workspace.set_state(Workspace_State.EXECUTING_BACKEND)

    workspace.deploy_differences(differences)
