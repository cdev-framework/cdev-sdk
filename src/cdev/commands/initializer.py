import json
import os
from pydantic.types import DirectoryPath
import shutil
from typing import Dict, Tuple, List

from rich.prompt import Prompt
from cdev.default.project import local_project
from cdev.cli.logger import set_global_logger_from_cli

from core.constructs.backend import Backend, Backend_Configuration
from core.constructs.workspace import Workspace_Info
from core.default.backend import Local_Backend_Configuration, LocalBackend


from ..constructs.project import Project_State, check_if_project_exists, project_info


STATE_FOLDER = "state"
INTERMEDIATE_FOLDER = 'intermediate'
CDEV_FOLDER = ".cdev"
CDEV_PROJECT_FILE = "cdev_project.json"
CENTRAL_STATE_FILE = "central_state.json"
SETTINGS_FOLDER_NAME = 'settings'
DEFAULT_ENVIRONMENTS = ["prod", "stage", "dev"]
TEMPLATE_LOCATIONS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'project_templates')


BASE_PROJECT_LOCATION = os.getcwd()

AVAILABLE_TEMPLATES = [
    'quick-start',
    'resources-test',
    'packages',
    'slack-bot',
    'user-auth',
    'power-tools'
]

def create_project_cli(args):
    config = args
    set_global_logger_from_cli(config.loglevel)

    if args.template:
        template_name = args.template

        if template_name not in AVAILABLE_TEMPLATES:
            print(f"{template_name} is not one of the available templates. {AVAILABLE_TEMPLATES}")
            return

    else:
        template_name = None

    create_project(args.name)
    print(f"Loading Template {template_name}")
    _load_template(template_name)
    

def _load_template(template_name: str):
    if not template_name:
        return

    template_folder_name = template_name.replace('-','_')


    if not template_folder_name in os.listdir(TEMPLATE_LOCATIONS):
        print(f"Could not finder template for {template_folder_name}")
        return

    template_location = os.path.join(TEMPLATE_LOCATIONS, template_folder_name)
    for x in os.listdir(template_location):
        
        full_location = os.path.join(template_location, x)
        if os.path.isdir(full_location):
            shutil.copytree(full_location, os.path.join(BASE_PROJECT_LOCATION, x))
        elif os.path.isfile(full_location):
            shutil.copyfile(full_location, os.path.join(BASE_PROJECT_LOCATION, x))


    print(f"Created Project From Template: {template_name}")

def create_project(project_name: str, base_directory: DirectoryPath = None):

    if not base_directory:
        base_directory = os.getcwd()

    if check_if_project_exists(base_directory):
        raise Exception("Project Already Created")


    _create_folder_structure(base_directory, DEFAULT_ENVIRONMENTS)

    base_settings_folder = os.path.join(base_directory, SETTINGS_FOLDER_NAME)
    


    backend_directory = os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER)
    backend_configuration = Local_Backend_Configuration(
        {
            "base_folder": backend_directory,
            "central_state_file": os.path.join(backend_directory, CENTRAL_STATE_FILE),
        }
    )

    new_project_info = project_info(
        project_name,
        environments=[],
        backend_info=backend_configuration,
        current_environment="",
    )

    project_info_location = os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)
    with open(project_info_location, "w") as fh:
        json.dump(new_project_info.dict(), fh, indent=4)

    new_project = local_project(project_info_location)

    new_project.initialize_project()

    # TODO restructure entire creating process so that this is more explicit
    base_dir = os.getcwd()

    for environment in DEFAULT_ENVIRONMENTS:

        environment_settings =  {
            "user_setting_module": [
                # set the settings modules as python modules
                os.path.relpath(os.path.join(base_settings_folder, f'base_settings.py'), start=base_dir)[:-3].replace('/',"."),
                os.path.relpath(os.path.join(base_settings_folder, f'{environment}_settings.py'), start=base_dir)[:-3].replace('/',".")
            ],
            "secret_dir":  os.path.relpath(os.path.join(base_settings_folder, f'{environment}_secrets'), start=base_dir),
        }

        new_project.create_environment(environment, environment_settings)
    

    new_project.set_state(Project_State.UNINITIALIZED)

    new_project.set_current_environment(DEFAULT_ENVIRONMENTS[-1])


def _create_folder_structure(base_directory: DirectoryPath, extra_settings: List[str]):
    """Create a skeleton file structure needed to make a project.

    Args:
        base_directory (DirectoryPath): [description]
        extra_settings (List[str]): [description]
    """

    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER)):
        os.mkdir(os.path.join(base_directory, CDEV_FOLDER))

    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER)):
        os.mkdir(os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER))

    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER, INTERMEDIATE_FOLDER)):
        os.mkdir(os.path.join(base_directory, CDEV_FOLDER, INTERMEDIATE_FOLDER))


    base_settings_folder = os.path.join(base_directory, SETTINGS_FOLDER_NAME)

    if not os.path.isdir(base_settings_folder):
        os.mkdir(base_settings_folder)

    with open(os.path.join( base_settings_folder, f'base_settings.py'), 'w'):
        pass

    with open(os.path.join( base_settings_folder, f'__init__.py'), 'w'):
        pass
    
    for environment in extra_settings:
        with open( os.path.join( base_settings_folder, f'{environment}_settings.py'), 'w' ):
            pass

        os.mkdir(os.path.join(base_settings_folder, f'{environment}_secrets'))


def load_project(args):
    base_directory = os.getcwd()

    project_info_location = os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)

    local_project(project_info_location)


def load_and_initialize_project(args):
    base_directory = os.getcwd()

    project_info_location = os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)

    local_project(project_info_location).initialize_project()
