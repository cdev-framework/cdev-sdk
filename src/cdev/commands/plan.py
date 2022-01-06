"""from ..backend import resource_state_manager, executer as backend_executer
from ..frontend import executer as frontend_executer
from ..output import print_plan
from ..utils import project, logger


log = logger.get_cdev_logger(__name__)


def plan_command(args):
    log.debug(f"Calling `cdev plan`")
    project.initialize_project()
    log.debug(f"Initialized project")
    #print("MADE IT HERE IN PLAN")
    rendered_frontend = frontend_executer.execute_frontend()
    log.debug(f"New rendered frontend -> {rendered_frontend}")
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    log.debug(f"Project differences -> {project_diffs}")

    diffs_valid  = backend_executer.validate_diffs(project_diffs)
    log.debug(f"Are project diffs valid -> {diffs_valid}")

    print_plan(rendered_frontend, project_diffs)
"""
