import json
import os
from pydantic.types import DirectoryPath
from typing import Dict, Tuple

from rich.prompt import Prompt
from cdev.constructs.environment import environment_info
from cdev.default.project import local_project
from core.constructs.backend import Backend, Backend_Configuration
from core.constructs.workspace import Workspace_Info

from core.default.backend import Local_Backend_Configuration, LocalBackend

from ..constructs.project import Project_State, check_if_project_exists, project_info


STATE_FOLDER = "state"
INTERMEDIATE_FOLDER = 'intermediate'
CDEV_FOLDER = ".cdev"
CDEV_PROJECT_FILE = "cdev_project.json"
CENTRAL_STATE_FILE = "central_state.json"
DEFAULT_ENVIRONMENTS = ["prod", "stage", "dev"]


AVAILABLE_TEMPLATES = [
    'quick-start',
    'test-resources'
]

def create_project_cli(args):

    print(args)
    if args.template:
        template_name = args.template

        if template_name not in AVAILABLE_TEMPLATES:
            print(f"{template_name} is not one of the available templates. {AVAILABLE_TEMPLATES}")
            return

    else:
        template_name = None

    create_project(args.name)
    print(f"Loading Template {template_name}")
    

    
        


def create_project(project_name: str, base_directory: DirectoryPath = None):

    if not base_directory:
        base_directory = os.getcwd()

    if check_if_project_exists(base_directory):
        raise Exception("Project Already Created")


    _create_folder_structure(base_directory)

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

    for environment in DEFAULT_ENVIRONMENTS:
        new_project.create_environment(environment)

    new_project.set_state(Project_State.UNINITIALIZED)

    new_project.set_current_environment(DEFAULT_ENVIRONMENTS[-1])


def _create_folder_structure(base_directory: DirectoryPath):

    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER)):
        os.mkdir(os.path.join(base_directory, CDEV_FOLDER))

    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER)):
        os.mkdir(os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER))

    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER, INTERMEDIATE_FOLDER)):
        os.mkdir(os.path.join(base_directory, CDEV_FOLDER, INTERMEDIATE_FOLDER))


def load_project(args):
    base_directory = os.getcwd()

    project_info_location = os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)

    local_project(project_info_location)


def load_and_initialize_project(args):
    base_directory = os.getcwd()

    project_info_location = os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)

    local_project(project_info_location).initialize_project()
