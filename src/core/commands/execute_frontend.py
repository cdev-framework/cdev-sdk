"""Utilities for creating a representation of a desired state of the workspace

"""
from typing import List, Tuple

from ..constructs.workspace import Workspace, Workspace_State
from ..constructs.components import Component_Difference
from ..constructs.resource import Resource_Difference, Resource_Reference_Difference
from ..constructs.output_manager import OutputManager

from core.utils.logger import log


def execute_frontend_cli(args):

    WORKSPACE = Workspace.instance()

    output_manager = OutputManager()


    
    execute_frontend(WORKSPACE, output_manager)



def execute_frontend(workspace: Workspace, output: OutputManager, previous_component_names: List[str]=None) -> Tuple[List[Component_Difference], List[Resource_Difference], List[Resource_Reference_Difference]]:

    log.debug("Executing Frontend")

    workspace.set_state(Workspace_State.EXECUTING_FRONTEND)
    current_state = workspace.generate_current_state()


    output.print_local_state(current_state)

    if not previous_component_names:
        diff_previous_component_names = [x.name for x in workspace.get_backend().get_resource_state(workspace.get_resource_state_uuid()).components]
    else:
        diff_previous_component_names = previous_component_names

    
    output.print_components_to_diff_against(diff_previous_component_names)

    differences = workspace.create_state_differences(current_state, diff_previous_component_names)


    if any(x for x in differences):
        output.print_state_differences(differences)

    else:
        print("No Differences")
        return None

    log.debug("Finish Executing Frontend")
    
    return differences
