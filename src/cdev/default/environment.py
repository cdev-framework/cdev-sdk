from core.constructs.workspace import Workspace, Workspace_State, initialize_workspace, load_workspace


from ..constructs.environment import Environment, environment_info
from core.default.cloudmapper import DefaultMapper

class local_environment(Environment):
    """
    A logically isolated instance of a project.
    """

    def __init__(self, info: environment_info) -> None:
        self.name = info.name
        self.workspace_info = info.workspace_info
        

    def get_workspace(self) -> Workspace:
        return Workspace.instance()

    def initialize_environment(self):
        ws = load_workspace(self.workspace_info)

        ws.set_state(Workspace_State.INITIALIZING)

        # Set the default mapper as a mapper in the workspace

        ws.add_mapper(DefaultMapper())

        initialize_workspace(ws, self.workspace_info.settings_info, self.workspace_info.config)

        ws.set_state(Workspace_State.INITIALIZED)

        
