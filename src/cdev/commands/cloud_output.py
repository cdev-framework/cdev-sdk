from cdev.constructs.project import Project

from core.commands.cloud_output import cloud_output_command as core_cloud_output_command
from core.constructs.output_manager import OutputManager


def cloud_output_command_cli(
    cloud_output_id: str,
    value: str,
    project: Project,
    output_manager: OutputManager,
    **kwargs
) -> None:
    cloud_output_command(cloud_output_id, value, project, output_manager)


def cloud_output_command(
    cloud_output_id: str,
    only_value: bool,
    project: Project,
    output_manager: OutputManager,
) -> None:
    ws = project.get_current_environment().get_workspace()
    core_cloud_output_command(ws, output_manager, cloud_output_id, only_value)
