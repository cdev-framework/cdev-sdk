from cdev.constructs.project import Project
from cdev.cli.logger import set_global_logger_from_cli
from cdev.default.output_manager import CdevOutputManager

from core.commands.run import run_command as core_run_command


def run_command_cli(args):
    config = args[0]
    set_global_logger_from_cli(config.loglevel)

    run_command(args[0])


def run_command(args):
    output_manager = CdevOutputManager()

    myProject = Project.instance()
    
    ws = myProject.get_current_environment().get_workspace()
    
    core_run_command(ws, output_manager, args)