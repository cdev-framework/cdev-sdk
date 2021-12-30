import os

from ..constructs.workspace import Workspace_Info

from ..default.workspace import local_workspace_manager



def initialize_workspace_cli(args):

    
    workspace_manager = local_workspace_manager(os.getcwd())
    
    workspace_config = workspace_manager.load_workspace_configuration()
    

    try:
        initialize_workspace(workspace_manager, workspace_config)
    except Exception as e:
        raise e


def initialize_workspace(workspace_manager: local_workspace_manager,  workspace_config: Workspace_Info):
    
    try:
        workspace_manager.load_workspace(workspace_config)
    except Exception as e:
        raise e






