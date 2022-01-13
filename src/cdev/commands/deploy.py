from ..constructs.project import Project

from core.commands.deploy_differences import execute_deployment


def deploy_command_cli(args):
    deploy_command(args)


def deploy_command(args):
    print(f"In deploy command")

    myProject = Project.instance()

    ws = myProject.get_current_environment().get_workspace()

    execute_deployment(ws)
