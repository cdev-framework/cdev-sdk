"""
All the commands available for use
"""

import os


from ..frontend import executer as frontend_executer
from ..backend import executer as backend_executer
from ..backend import resource_state_manager
from ..backend import initializer
from ..utils import project
from ..utils.logger import get_cdev_logger

log = get_cdev_logger(__name__)


def plan():

    log.debug(f"Calling `cdev plan`")
    project.initialize_project()
    log.debug(f"Initialized project")
    rendered_frontend = frontend_executer.execute_frontend()
    log.debug(f"New rendered frontend -> {rendered_frontend}")
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    log.debug(f"Project differences -> {project_diffs}")

    diffs_valid  = backend_executer.validate_diffs(project_diffs)
    log.debug(f"Are project diffs valid -> {diffs_valid}")

def deploy():
    project.initialize_project()
    rendered_frontend = frontend_executer.execute_frontend()
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    if backend_executer.validate_diffs(project_diffs):
        backend_executer.deploy_diffs(project_diffs)

    return 


def init():
    print("INIT")
    initializer.initialize_backend(os.getcwd())
    return

