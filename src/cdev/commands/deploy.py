from cdev.constructs.project import Project
from cdev.cli.logger import set_global_logger_from_cli

from core.constructs.output_manager import OutputManager

from core.commands.deploy_differences import execute_deployment


def deploy_command_cli(
    project: Project, output_manager: OutputManager, **kwargs
) -> None:
    deploy_command(project, output_manager)


def deploy_command(project: Project, output_manager: OutputManager) -> None:
    ws = project.get_current_environment().get_workspace()
    execute_deployment(ws, output_manager)
