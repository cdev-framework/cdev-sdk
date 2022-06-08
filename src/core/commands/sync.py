from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager
from core.constructs.workspace_watcher import WorkspaceWatcher


def execute_sync(args) -> None:
    ws = Workspace.instance()

    output_manager = OutputManager()

    core_sync_command(ws, output_manager, args)


def core_sync_command(workspace: Workspace, output: OutputManager, cli_args) -> None:
    """
    Attempts to find and run a user defined command

    format:
    cdev sync <sub_command> <args>
    """
    ignore_args = cli_args[0].ignore
    watch_args = cli_args[0].watch
    no_default_args = cli_args[0].no_default
    try:
        workspace_watcher = WorkspaceWatcher(
            workspace,
            output,
            no_default=no_default_args,
            patterns_to_watch=watch_args,
            patterns_to_ignore=ignore_args,
        )
        workspace_watcher.watch()
    except Exception as e:
        print(e)
        return
