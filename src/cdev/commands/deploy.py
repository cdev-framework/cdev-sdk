from ..constructs.project import Project

from core.commands.deploy_differences import execute_deployment

from ..output.output_manager import CdevOutputManager

def deploy_command_cli(args):
    deploy_command(args)


def deploy_command(args):

    output_manager = CdevOutputManager()
    myProject = Project.instance()

    ws = myProject.get_current_environment().get_workspace()

    execute_deployment(ws, output_manager)
