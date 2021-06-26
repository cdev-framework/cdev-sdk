import os

import cdev.fs_manager.finder as fs
import cdev.fs_manager.project_initializer as initalizer

from . import state_manager as local_state_manager
from . import executer


"""
This files contains the implementation of the different commands available to the CLI. 

Theses commands should take only a params object that defines different options and configurations for the command
"""

def plan():
    print("PLAN")
    #folder_information = fs.parse_folder(os.path.join(".", "src"))
    #return local_state_manager.update_local_state(folder_information)

    rv = executer.execute_cdev_project()
    return rv

def init():
    print("INIT")
    initalizer.initialize_project(os.getcwd())
    return

