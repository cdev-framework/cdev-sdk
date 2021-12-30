import os
import sys
from typing import Dict
import uuid


from core.default.workspace import local_workspace

from ..constructs import workspace as workspace_tests

# Monkey patch the file location to be ./tmp
base_dir = os.path.join(os.path.dirname(__file__), "tmp")

# Insert the path to the local data file
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))


def local_workspace_config_factory() -> Dict:
    tmp = str(uuid.uuid4())
    new_base = os.path.join(base_dir, tmp)
    new_state_file = os.path.join(new_base, "local_state.json")

    os.mkdir(new_base)
    return {
        "backend_configuration": {
            "python_module": "core.default.backend",
            "python_class": "LocalBackend",
            "config":{
                "base_folder": new_base,
                "central_state_file": new_state_file
            }
        },
        "initialization_file": "example_init"
    }
        




def test_initialize_workspace():
    workspace = local_workspace()
    workspace_config = local_workspace_config_factory()

    workspace_tests.simple_initialize_workspace(workspace, workspace_config)




def test_add_component():
    workspace = local_workspace()
    workspace_config = local_workspace_config_factory()

    workspace_tests.simple_execute_frontend_workspace(workspace, workspace_config)



def test_add_commands():
    workspace = local_workspace()
    workspace_config = local_workspace_config_factory()

    workspace_tests.simple_add_commands(workspace, workspace_config)
