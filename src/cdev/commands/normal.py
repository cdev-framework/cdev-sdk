"""
All the commands available for use
"""


import os
from cdev.settings import SETTINGS
from cdev.utils.hasher import hash_string

import shutil


from ..utils import project
from ..utils.logger import get_cdev_logger
from ..utils import environment as cdev_environment

from cdev.output import print_plan, confirm_deployment, print, confirm_destroy

from ..frontend import executer as frontend_executer
from ..backend import executer as backend_executer
from ..backend import resource_state_manager, cloud_mapper_manager
from ..constructs import Cdev_Project


log = get_cdev_logger(__name__)


def plan(args):
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


def deploy(args):
    project.initialize_project()
    rendered_frontend = frontend_executer.execute_frontend()
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    


    if not backend_executer.validate_diffs(project_diffs):
        raise Exception 

    print_plan(rendered_frontend, project_diffs)

    if not project_diffs:
        print("No differences to deploy")
        return

    if not confirm_deployment():
        raise Exception

    backend_executer.deploy_diffs(project_diffs)
    output({})

    return 


def destroy(args):
    if not confirm_destroy():
        return

    shutil.rmtree(os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME")))





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


def output(args):
    log.debug(f"Calling `cdev output`")
    project.initialize_project()
    log.debug(f"Initialized project")
    #print("MADE IT HERE IN PLAN")
    rendered_frontend = frontend_executer.execute_frontend()
    
    PROJECT = Cdev_Project()
    
    desired_outputs = PROJECT.get_outputs()

    rendered_outputs = []

    for label, output in desired_outputs.items(): 
        
        identifier = output.resource.split("::")[-1]

        if output.transformer:
            rendered_value = cloud_mapper_manager.get_output_value(identifier, output.key, transformer=output.get("transformer"))
        else:
            rendered_value = cloud_mapper_manager.get_output_value(identifier, output.key)

        rendered_outputs.append(f"[magenta]{label}[/magenta] -> [green]{rendered_value}[/green]")

    print(f"---OUTPUTS---")
    for rendered_output in rendered_outputs:
        print(rendered_output)
        


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




