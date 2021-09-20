import os
import shutil

from ..output import confirm_destroy
from ..settings import SETTINGS

def destroy_command(args):
    if not confirm_destroy():
        return

    shutil.rmtree(os.path.join(SETTINGS.get("INTERNAL_FOLDER_NAME")))


