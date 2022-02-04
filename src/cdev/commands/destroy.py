from ..constructs.project import Project

from core.commands.deploy_differences import execute_deployment

from cdev.default.output_manager import CdevOutputManager

def destroy_command_cli(args):
    destroy_command(args)


def destroy_command(args):

    output_manager = CdevOutputManager()
    myProject = Project.instance()

    print(f"Destory")

