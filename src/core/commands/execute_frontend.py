from ..constructs.workspace import Workspace



def execute_frontend(args):
    
    WORKSPACE = Workspace.instance()
    print(WORKSPACE)
    current_state = WORKSPACE.generate_current_state()
    
    print(current_state)