from pydantic import BaseModel

from core.constructs.workspace import Workspace, Workspace_Info


class environment_info(BaseModel):
    """
    Represents the information about an environment.

    Arguments:
        name (str): Name of this environment
        workspace_info (Workspace_Info): The information needed to load the Workspace for this environment
    """

    name: str
    workspace_info: Workspace_Info

    def __init__(__pydantic_self__, name: str, workspace_info: Workspace_Info) -> None:

        super().__init__(**{"name": name, "workspace_info": workspace_info})


class Environment:
    """
    A logically isolated instance of a project.
    """

    def __init__(self, info: environment_info) -> None:
        pass

    def get_name(self) -> str:
        """Return the name of the Environment

        Returns:
            str: name of the Environment
        """
        raise NotImplementedError

    def get_workspace(self) -> Workspace:
        """Get the Workspace associated with this Environment

        Returns:
            Workspace
        """
        raise NotImplementedError

    def initialize_environment(self) -> None:
        """Initialize the Environment"""
        raise NotImplementedError
