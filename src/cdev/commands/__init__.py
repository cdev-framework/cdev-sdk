"""
All the commands available for use
"""

import os
from rich.console import Console

from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

from cdev.utils.hasher import hash_string




from ..utils import project
from ..utils.logger import get_cdev_logger
from ..utils import environment as cdev_environment

from cdev.output import print_plan, confirm_deployment, print

log = get_cdev_logger(__name__)

from ..frontend import executer as frontend_executer
from ..backend import executer as backend_executer
from ..backend import resource_state_manager

def plan(args):
    log.debug(f"Calling `cdev plan`")
    project.initialize_project()
    log.debug(f"Initialized project")
    print("MADE IT HERE IN PLAN")
    rendered_frontend = frontend_executer.execute_frontend()
    log.debug(f"New rendered frontend -> {rendered_frontend}")
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    log.debug(f"Project differences -> {project_diffs}")

    diffs_valid  = backend_executer.validate_diffs(project_diffs)
    log.debug(f"Are project diffs valid -> {diffs_valid}")

    print_plan(rendered_frontend, project_diffs)


def deploy(args):
    from ..frontend import executer as frontend_executer
    from ..backend import executer as backend_executer
    from ..backend import resource_state_manager


    project.initialize_project()
    rendered_frontend = frontend_executer.execute_frontend()
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    


    if not backend_executer.validate_diffs(project_diffs):
        raise Exception 

    print_plan(rendered_frontend, project_diffs)

    if not project_diffs:
        print("No differences to deploy")
        return

    #if not confirm_deployment():
    #    raise Exception

    backend_executer.deploy_diffs(project_diffs)

    return 


def init(args):
    base_project_dir = os.getcwd()

    info = project.project_definition(base_project_dir, "demo-project", ['prod', 'stage', 'dev_daniel'])

    project.create_new_project(info)

    return


def environment(command, args):
    parsed_args = vars(args)
    
    if command == '':
        print("You must provide a sub-command. run `cdev environment --help` for more information on available subcommands")
    elif command == 'ls':
        current_env = cdev_environment.get_current_environment()

        for env in cdev_environment.get_environment_info_object().environments:
            if env.name == current_env:
                print(f"> {env.name}")
            else:
                print(env.name)
    elif command == 'get':
        print(cdev_environment.get_environment_info(parsed_args.get("env")))
    elif command == 'set':
        cdev_environment.set_current_environment(parsed_args.get("env"))
    elif command == 'create':
        cdev_environment.create_environment(parsed_args.get("env"))


def user(command, args):
    parsed_args = vars(args)
    
    if command == '':
        print("You must provide a sub-command. run `cdev environment --help` for more information on available subcommands")
    elif command == 'ls':
        pass
    elif command == 'get':
        pass
    elif command == 'set':
        pass
    elif command == 'create':
        pass




