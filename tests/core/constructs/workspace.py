from typing import Dict
from core.constructs.workspace import Workspace, Workspace_State, Workspace_Info

from .. import sample_data

def simple_initialize_workspace(workspace: Workspace, config: Dict):
    workspace.set_state(Workspace_State.INITIALIZING)
    workspace.initialize_workspace(config)
    


def simple_execute_frontend_workspace(workspace: Workspace, config: Workspace_Info):
    components = sample_data.simple_components()

    workspace.set_state(Workspace_State.INITIALIZING)

    for component in components:
        workspace.add_component(component)

    
    workspace.initialize_workspace(config)
    workspace.set_state(Workspace_State.INITIALIZED)
    workspace.set_state(Workspace_State.EXECUTING_FRONTEND)

    state = workspace.generate_current_state()

    assert len(state) == len(components)


def simple_add_commands(workspace: Workspace, config: Workspace_Info):
    commands = sample_data.simple_commands()

    workspace.set_state(Workspace_State.INITIALIZING)

    for command in commands:
        workspace.add_command(command)


    workspace.initialize_workspace(config)

    workspace.set_state(Workspace_State.INITIALIZED)

    returned_commands = workspace.get_commands()

    assert len(commands) == len(returned_commands)
