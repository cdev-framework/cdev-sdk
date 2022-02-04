from cdev.default.output_manager import CdevOutputManager
from cdev.constructs.project import Project

from core.commands.execute_frontend import execute_frontend
from core.utils import logger


def plan_command_cli(args):
    plan_command(args)


def plan_command(args):
    output_manager = CdevOutputManager()

    myProject = Project.instance()
    
    ws = myProject.get_current_environment().get_workspace()

    
    log = logger.cdev_logger(is_rich_formatted=False)
    logger.set_global_logger(log)
    execute_frontend(ws, output_manager)

  
