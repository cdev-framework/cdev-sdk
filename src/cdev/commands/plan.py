from cdev.constructs.project import Project
from cdev.cli.logger import set_global_logger_from_cli
from cdev.default.output_manager import CdevOutputManager

from core.commands.execute_frontend import execute_frontend
from core.utils.logger import log


def plan_command_cli(args) -> None:
    config = args[0]
    set_global_logger_from_cli(config.loglevel)

    plan_command({})


def plan_command(args) -> None:
    log.info(msg="Starting Plan Command")
    output_manager = CdevOutputManager()

    my_project = Project.instance()
    log.debug("Loaded Project Global Instance")

    ws = my_project.get_current_environment().get_workspace()

    execute_frontend(ws, output_manager)
    log.info("Finished Plan Command")
