from typing import List

from cdev.constructs.project import Project

from core.commands.run import run_command as core_run_command
from core.constructs.output_manager import OutputManager


def run_command_cli(
    subcommand: str = None,
    subcommand_args: List[str] = None,
    project: Project = None,
    output_manager: OutputManager = None,
    **kwargs
) -> None:

    run_command(subcommand, subcommand_args, project, output_manager)


def run_command(
    subcommand: str,
    subcommand_args: List[str],
    project: Project,
    output_manager: OutputManager,
) -> None:
    ws = project.get_current_environment().get_workspace()
    core_run_command(
        subcommand=subcommand,
        subcommand_args=subcommand_args,
        workspace=ws,
        output=output_manager,
    )
