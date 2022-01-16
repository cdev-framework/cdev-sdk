from networkx.classes import digraph
from typing import List

from core.output.output_manager import OutputManager
from ..constructs.workspace import Workspace, Workspace_State

import networkx as nx




def execute_frontend_cli(args):

    WORKSPACE = Workspace.instance()

    output_manager = OutputManager()

    execute_frontend(WORKSPACE, output_manager)


def execute_frontend(workspace: Workspace, output: OutputManager, previous_component_names: List[str]=None) -> nx.DiGraph:
    workspace.set_state(Workspace_State.EXECUTING_FRONTEND)
    current_state = workspace.generate_current_state()

    output.print_local_state(current_state)

    if not previous_component_names:
        diff_previous_component_names = [x.name for x in workspace.get_backend().get_resource_state(workspace.get_resource_state_uuid()).components]
    else:
        diff_previous_component_names = previous_component_names

    differences = workspace.create_state_differences(current_state, diff_previous_component_names)


    


    differences_ordered = workspace.sort_differences(differences)

    return differences_ordered
