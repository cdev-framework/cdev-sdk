import json
import os
from pydantic.types import DirectoryPath
from typing import Dict, Tuple

from rich.prompt import Prompt
from cdev.constructs.environment import environment_info
from core.constructs.backend import Backend, Backend_Configuration
from core.constructs.workspace import Workspace_Info

from core.default.backend import Local_Backend_Configuration, LocalBackend

from ..constructs.project import check_if_project_exists, project_info


STATE_FOLDER = "state"
CDEV_FOLDER = ".cdev"
CDEV_PROJECT_FILE = "cdev_project.json"
CENTRAL_STATE_FILE = "central_state.json"

      

def init_project_cli(args):
    print(args)
    init_project(args.name)


def init_project(project_name: str, base_directory: DirectoryPath=None):

    if not base_directory:
        base_directory = os.getcwd()


    if check_if_project_exists(base_directory):
        raise Exception("Project Already Created")


    print(f"Create project")

    _create_folder_structure(base_directory)

    backend_directory = os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER)
    backend_configuration, backend = _create_local_backend(backend_directory)

    workspace_config = {
        'backend_configuration': backend_configuration.dict()
    }

    environment_info = _create_environment('demo', backend, workspace_config)

    new_project_info = project_info(
        project_name,
        environments=[environment_info],
        backend_info=backend_configuration,
        current_environment='demo'
    )


    with open(os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE), 'w') as fh:
        json.dump(new_project_info.dict(), fh, indent=4)




def _create_folder_structure(base_directory: DirectoryPath):
    
    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER)):
        os.mkdir(os.path.join(base_directory, CDEV_FOLDER))


    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER)):
        os.mkdir(os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER))
    

def _create_local_backend(backend_directory: DirectoryPath) -> Tuple[Local_Backend_Configuration, Backend]:
    backend = LocalBackend(backend_directory, os.path.join(backend_directory, CENTRAL_STATE_FILE))


    return Local_Backend_Configuration({
        "base_folder": backend_directory,
        "central_state_file": CENTRAL_STATE_FILE
    }), backend
    


def _create_environment(environment_name: str, backend: Backend, workspace_config: Dict={}) -> environment_info:
    resource_state_id = backend.create_resource_state(environment_name)

    workspace_config['resource_state_uuid'] = resource_state_id
    workspace_config['initialization_module'] = 'cdev_project'

    return environment_info(
        environment_name,
        Workspace_Info(
            "core.default.workspace",
            "local_workspace",
            workspace_config
        )
    )
