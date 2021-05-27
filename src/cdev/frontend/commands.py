import os

import cdev.fs_manager.finder as fs
import cdev.fs_manager.project_initializer as initalizer

from . import state_manager as local_state_manager


def plan():
    print("PLAN")
    folder_information = fs.parse_folder(os.path.join(".", "src"))

    local_state_manager.update_local_state(folder_information)

    return

def init():
    print("INIT")
    initalizer.initialize_project(os.getcwd())
    return

