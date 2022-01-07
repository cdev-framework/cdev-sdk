
from core.constructs.workspace import Workspace


from ..constructs.environment import Environment, environment_info
from core.constructs.workspace import load_and_initialize_workspace


class local_environment(Environment):
    """
    A logically isolated instance of a project. 
    """
    def __init__(self, info: environment_info) -> None:
        self.name = info.name
        self.workspace_info = info.workspace_info
        self.settings = info.settings
        pass


    def get_workspace(self) -> Workspace:
        return Workspace.instance()

    
    def initialize_environment(self):
        print(f"initializing environment")
        load_and_initialize_workspace(self.workspace_info)
