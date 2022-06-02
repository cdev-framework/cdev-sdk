from cdev.constructs.project import Project
from cdev.default.output_manager import CdevOutputManager
from cdev.cli.logger import set_global_logger_from_cli

from core.commands.sync import core_sync_command


def sync_command_cli(args) -> None:
    config = args[0]
    set_global_logger_from_cli(config.loglevel)
    sync_command(args)


def sync_command(args) -> None:

    output_manager = CdevOutputManager()
    my_project = Project.instance()
    ws = my_project.get_current_environment().get_workspace()
    core_sync_command(ws, output_manager, args)
