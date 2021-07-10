import os


from cdev.frontend import executer as frontend_executer
from cdev.backend import executer as backend_executer
from cdev.backend import resource_state_manager
from cdev.backend import initializer
from cdev.utils import project

"""
Some doc string
"""

def plan():

    project.initialize_project()
    rendered_frontend = frontend_executer.execute_frontend()
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    backend_executer.validate_diffs(project_diffs)
     

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

