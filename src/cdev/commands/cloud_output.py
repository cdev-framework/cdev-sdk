from ..constructs.project import Project

from core.commands.deploy_differences import execute_deployment

from cdev.default.output_manager import CdevOutputManager

def cloud_output_command_cli(args):
    cloud_output_command(args)


def cloud_output_command(args):

    output_manager = CdevOutputManager()
    myProject = Project.instance()

    print(f"Cloud Output")

