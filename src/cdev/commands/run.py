from cdev.output.output_manager import CdevOutputManager
from ..constructs.project import Project

from core.commands.run import run_command as core_run_command


def run_command_cli(args):
    run_command(args[0])


def run_command(args):
    output_manager = CdevOutputManager()

    myProject = Project.instance()
    
    ws = myProject.get_current_environment().get_workspace()

    core_run_command(ws, output_manager, args)