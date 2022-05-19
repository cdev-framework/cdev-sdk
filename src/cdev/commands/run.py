from cdev.constructs.project import Project
from cdev.cli.logger import set_global_logger_from_cli
from cdev.default.output_manager import CdevOutputManager

from core.commands.run import run_command as core_run_command


def run_command_cli(args) -> None:
    config = args[0]
    set_global_logger_from_cli(config.loglevel)

    run_command(args[0])


def run_command(args) -> None:

    my_project = Project.instance()
    ws = my_project.get_current_environment().get_workspace()

    output_manager = CdevOutputManager()
    core_run_command(ws, output_manager, args)
