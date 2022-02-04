from cdev.constructs.project import Project
from cdev.default.output_manager import CdevOutputManager
from cdev.cli.logger import set_global_logger_from_cli

from core.commands.deploy_differences import execute_deployment

def destroy_command_cli(args):
    config = args[0]
    set_global_logger_from_cli(config.loglevel)
    destroy_command(args)


def destroy_command(args):

    output_manager = CdevOutputManager()
    myProject = Project.instance()

    print(f"Destory")

