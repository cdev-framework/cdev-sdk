import os


from cdev.frontend import executer as frontend_executer
from cdev.backend import executer as backend_executer
from cdev.backend import initializer
from cdev.utils import project

"""
Some doc string
"""

def plan():

    project.initialize_project()
    rendered_frontend = frontend_executer.execute_frontend()
    backend_executer.create_diffs(rendered_frontend)

    return {}

def init():
    print("INIT")
    initializer.initialize_backend(os.getcwd())
    return

