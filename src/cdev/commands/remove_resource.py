from cdev.constructs.project import Project

from core.commands.remove_resource import (
    remove_resource_command as remove_resource_command_core,
)
from core.constructs.output_manager import OutputManager


def remove_resource_command_cli(
    cloud_output_id: str,
    force: bool,
    project: Project,
    output_manager: OutputManager,
    **kwargs
) -> None:
    remove_resource_command(cloud_output_id, force, project, output_manager)


def remove_resource_command(
    cloud_output_id: str,
    force: bool,
    project: Project,
    output_manager: OutputManager,
) -> None:
    ws = project.get_current_environment().get_workspace()
    remove_resource_command_core(ws, output_manager, cloud_output_id, force)
