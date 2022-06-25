from cdev.constructs.project import Project

from core.commands.execute_frontend import execute_frontend
from core.constructs.output_manager import OutputManager


def plan_command_cli(project: Project, output_manager: OutputManager, **kwargs) -> None:
    plan_command(project, output_manager)


def plan_command(project: Project, output_manager: OutputManager) -> None:
    ws = project.get_current_environment().get_workspace()
    execute_frontend(ws, output_manager)
