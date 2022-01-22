from cdev.output.output_manager import CdevOutputManager
from ..constructs.project import Project

from core.commands.execute_frontend import execute_frontend


def plan_command_cli(args):
    plan_command(args)


def plan_command(args):
    output_manager = CdevOutputManager()

    myProject = Project.instance()
    
    ws = myProject.get_current_environment().get_workspace()

    execute_frontend(ws, output_manager)
