from cdev.constructs.project import Project
from core.constructs.output_manager import OutputManager
from core.commands.deploy_differences import execute_deployment


def deploy_command_cli(
        disable_prompt: bool,
        project: Project, output_manager: OutputManager, **kwargs
) -> None:
    deploy_command(disable_prompt, project, output_manager)


def deploy_command(
    disable_prompt: bool,
    project: Project,
    output_manager: OutputManager
) -> None:
    ws = project.get_current_environment().get_workspace()
    execute_deployment(ws, output_manager, no_prompt=disable_prompt)
