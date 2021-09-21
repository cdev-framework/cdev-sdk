from ..backend import resource_state_manager, executer as backend_executer
from ..frontend import executer as frontend_executer
from .. import output as cdev_output
from ..utils import project, logger

from . import cloud_output


log = logger.get_cdev_logger(__name__)



def deploy_command(args):
    project.initialize_project()
    rendered_frontend = frontend_executer.execute_frontend()
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)

    if not backend_executer.validate_diffs(project_diffs):
        raise Exception 

    cdev_output.print_plan(rendered_frontend, project_diffs)

    if not project_diffs:
        cdev_output.print("No differences to deploy")
        return

    if not cdev_output.confirm_deployment():
        raise Exception

    backend_executer.deploy_diffs(project_diffs)
    cloud_output.cloud_output_command({})

    return



def local_deploy_command(args):
    project.initialize_project()
    rendered_frontend = frontend_executer.execute_frontend()
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)

    if not backend_executer.validate_diffs(project_diffs):
        raise Exception 


    if not project_diffs:
        cdev_output.print("No differences to deploy")
        return

    cdev_output.print_plan(rendered_frontend, project_diffs)
    
    backend_executer.deploy_diffs(project_diffs)
    
    return
