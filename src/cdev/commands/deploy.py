from cdev.constructs.project import Project
from cdev.default.output_manager import CdevOutputManager
from cdev.cli.logger import set_global_logger_from_cli

from core.commands.deploy_differences import execute_deployment



def deploy_command_cli(args):
    config = args[0]
    set_global_logger_from_cli(config.loglevel)
    deploy_command(args)


def deploy_command(args):

    output_manager = CdevOutputManager()
    myProject = Project.instance()

    ws = myProject.get_current_environment().get_workspace()

    execute_deployment(ws, output_manager)
