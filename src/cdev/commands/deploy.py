from cdev.constructs.project import Project
from cdev.default.output_manager import CdevOutputManager
from cdev.cli.logger import set_global_logger_from_cli

from core.commands.deploy_differences import execute_deployment


def deploy_command_cli(args) -> None:
    config = args[0]
    set_global_logger_from_cli(config.loglevel)
    deploy_command(args)


def deploy_command(cli_args) -> None:

    output_manager = CdevOutputManager()
    my_project = Project.instance()

    ws = my_project.get_current_environment_workspace()

    no_prompt = cli_args[0].disable_prompt
    execute_deployment(ws, output_manager, no_prompt=no_prompt)
