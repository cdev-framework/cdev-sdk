"""
All the commands available for use
"""

import os

import cdev


from ..frontend import executer as frontend_executer
from ..backend import executer as backend_executer
from ..backend import resource_state_manager
from ..backend import initializer
from ..utils import project
from ..utils.logger import get_cdev_logger
from ..utils import environment as cdev_environment

log = get_cdev_logger(__name__)


def plan(args):
    print(f"plan -> {args}")
    #log.debug(f"Calling `cdev plan`")
    #project.initialize_project()
    #log.debug(f"Initialized project")
    #rendered_frontend = frontend_executer.execute_frontend()
    #log.debug(f"New rendered frontend -> {rendered_frontend}")
    #project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    #log.debug(f"Project differences -> {project_diffs}")
#
    #diffs_valid  = backend_executer.validate_diffs(project_diffs)
    #log.debug(f"Are project diffs valid -> {diffs_valid}")

def deploy(args):
    print(f"deploy -> {args}")
    #project.initialize_project()
    #rendered_frontend = frontend_executer.execute_frontend()
    #project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    #if backend_executer.validate_diffs(project_diffs):
    #    backend_executer.deploy_diffs(project_diffs)
#
    #return 


def init(args):
    print(f"init -> {args}")
    #base_project_dir = os.getcwd()
#
    #info = project.project_definition(base_project_dir, "demo-project", ['prod', 'stage', 'dev_daniel'])
#
    #project.create_new_project(info)
#
    #return


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


    
