from ..constructs.workspace import Workspace



def execute_frontend_cli(args):
    
    WORKSPACE = Workspace.instance()

    execute_frontend(WORKSPACE)
    


def execute_frontend(workspace: Workspace):
    current_state = workspace.generate_current_state()
    
    print(current_state)