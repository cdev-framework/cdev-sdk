from networkx.classes import digraph
from ..constructs.workspace import Workspace, Workspace_State

import networkx as nx


def execute_frontend_cli(args):

    WORKSPACE = Workspace.instance()

    execute_frontend(WORKSPACE)


def execute_frontend(workspace: Workspace) -> nx.DiGraph:
    workspace.set_state(Workspace_State.EXECUTING_FRONTEND)
    current_state = workspace.generate_current_state()

    print(current_state)

    all_previous_component_names = [x.name for x in workspace.get_backend().get_resource_state(workspace.get_resource_state_uuid()).components]
    print(f"All previous components")

    differences = workspace.create_state_differences(current_state, all_previous_component_names)


    print(differences)


    differences_ordered = workspace.sort_differences(differences)

    return differences_ordered
