from cdev.constructs.project import Project
from cdev.default.output_manager import CdevOutputManager
from cdev.cli.logger import set_global_logger_from_cli

from core.commands.deploy_differences import execute_deployment


def deploy_command_cli(args) -> None:
    config = args[0]
    set_global_logger_from_cli(config.loglevel)
    deploy_command(args)


def deploy_command(args) -> None:

    my_project = Project.instance()
    ws = my_project.get_current_environment().get_workspace()

    output_manager = CdevOutputManager()
    execute_deployment(ws, output_manager)
