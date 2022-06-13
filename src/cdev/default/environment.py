from core.constructs.workspace import (
    Workspace,
    initialize_workspace,
    load_workspace,
)

from ..constructs.environment import Environment, environment_info


class local_environment(Environment):
    """
    A logically isolated instance of a project.
    """

    def __init__(self, info: environment_info) -> None:
        self.name = info.name
        self.workspace_info = info.workspace_info
        self._loaded_workspace = load_workspace(self.workspace_info)

    def get_name(self) -> str:
        return self.name

    def get_workspace(self) -> Workspace:
        return self._loaded_workspace

    def initialize_environment(self) -> None:
        initialize_workspace(self._loaded_workspace, self.workspace_info)
