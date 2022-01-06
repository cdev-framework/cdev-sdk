"""import os
import shutil


from ..backend import executer as backend_executer, resource_state_manager
from .. import output
from ..settings import SETTINGS

from ..models import Rendered_State

from ..utils import project, logger



log = logger.get_cdev_logger(__name__)


def destroy_command(args):
    project.initialize_project()
    if not output.confirm_destroy():
        return

    fake_rendered_frontend = Rendered_State(**{
        "hash": 0,
        "rendered_components": None
    })

    fake_project_diffs = resource_state_manager.create_project_diffs(fake_rendered_frontend)
    #print(fake_project_diffs)
    backend_executer.deploy_diffs(fake_project_diffs)
    output.print("Removed resources in environment")
    #shutil.rmtree(os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME")))


"""
