from typing import List, Dict

from pydantic import BaseModel
from pydantic.types import FilePath

from core.constructs.workspace import Workspace, Workspace_Info




class environment_info(BaseModel):
    """
    Represents the information about an environment.

    Arguments:
        name (str): Name of this environment
        workspace_info (Workspace_Info): The information needed to load the Workspace for this environment
        settings (Dict): Any settings to override within the environment
    """

    name: str
    workspace_info: Workspace_Info
    settings: Dict

    def __init__(
        __pydantic_self__,
        name: str,
        workspace_info: Workspace_Info,
        settings: Dict = {},
    ) -> None:

        super().__init__(
            **{"name": name, "workspace_info": workspace_info, "settings": settings}
        )


class Environment:
    """
    A logically isolated instance of a project.
    """

    def __init__(self, info: environment_info) -> None:
        pass

    def get_workspace(self) -> Workspace:
        raise NotImplementedError

    def initialize_environment(self):
        raise NotImplementedError
