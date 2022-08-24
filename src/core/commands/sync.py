from cdev.constructs.project import Project
from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager
from core.constructs.workspace_watcher import WorkspaceWatcher


def execute_sync(
    disable_prompt: bool,
    no_default: bool,
    watch: str,
    ignore: str,
    ws: Workspace,
    output_manager: OutputManager,
) -> None:
    core_sync_command(disable_prompt, no_default, watch, ignore, ws, output_manager)


def core_sync_command(
    disable_prompt: bool,
    no_default: bool,
    watch: str,
    ignore: str,
    workspace: Workspace,
    output_manager: OutputManager,
) -> None:
    """
    watch the filesystem for changes and then run the deploy command
    """
    try:
        workspace_watcher = WorkspaceWatcher(
            workspace,
            output_manager,
            no_prompt=disable_prompt,
            no_default=no_default,
            patterns_to_watch=watch,
            patterns_to_ignore=ignore,
        )
        workspace_watcher.watch()
    except Exception as e:
        return
