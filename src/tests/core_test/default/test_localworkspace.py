import os
import sys
from typing import Dict
import uuid
from core.constructs.backend import Backend_Configuration
from core.constructs.settings import Settings_Info


from core.default.workspace import local_workspace
from core.constructs.workspace import Workspace_Info

from ..constructs import test_workspace as workspace_tests

# Monkey patch the file location to be ./tmp
base_dir = os.path.join(os.path.dirname(__file__), "tmp")

# Insert the path to the local data file
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))


# def local_workspace_info_factory() -> Workspace_Info:
#    tmp = str(uuid.uuid4())
#    new_base = os.path.join(base_dir, tmp)
#    new_state_file = os.path.join(new_base, "local_state.json")
#
#    os.mkdir(new_base)
#
#    return Workspace_Info(
#        python_module="",
#        python_class="",
#        settings_info=Settings_Info(
#
#        ),
#        backend_info=Backend_Configuration(
#
#        ),
#        resource_state_uuid="",
#    )
#
#
#
# def test_initialize_workspace():
#    workspace = local_workspace()
#    workspace_config = local_workspace_info_factory()
#
#    workspace_tests.simple_initialize_workspace(workspace, workspace_config)
#
#
# def test_execute_frontend():
#    workspace = local_workspace()
#    workspace_config = local_workspace_info_factory()
#
#    workspace_tests.simple_execute_frontend_workspace(workspace, workspace_config)
#
#
# def test_add_commands():
#    workspace = local_workspace()
#    workspace_config = local_workspace_info_factory()
#
#    workspace_tests.simple_add_commands(workspace, workspace_config)
#
