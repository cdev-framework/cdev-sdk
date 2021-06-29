import os


from cdev.frontend import executer as frontend_executer
from cdev.backend import executer as backend_executer

"""
Some doc string
"""

def plan():
    print("PLAN2")

    rendered_frontend = frontend_executer.execute_frontend()
    #backend_executer.create_diffs(rendered_frontend)

    return {}

def init():
    print("INIT")
    #initalizer.initialize_project(os.getcwd())
    return

