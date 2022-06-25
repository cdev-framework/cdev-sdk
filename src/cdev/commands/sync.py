from cdev.constructs.project import Project

from core.commands.sync import core_sync_command
from core.constructs.output_manager import OutputManager


def sync_command_cli(
    disable_prompt: bool,
    no_default: bool,
    watch: str,
    ignore: str,
    project: Project,
    output_manager: OutputManager,
    **kwargs
) -> None:
    sync_command(disable_prompt, no_default, watch, ignore, project, output_manager)


def sync_command(
    disable_prompt: bool,
    no_default: bool,
    watch: str,
    ignore: str,
    project: Project,
    output_manager: OutputManager,
) -> None:
    ws = project.get_current_environment().get_workspace()
    core_sync_command(disable_prompt, no_default, watch, ignore, ws, output_manager)
