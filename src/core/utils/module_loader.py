"""
Utilities to help standardize how the framework dynamically imports code
"""

import sys
import importlib
from types import ModuleType
import sys
from typing import TextIO


def import_module(module_name: str, denote_output: bool = False) -> ModuleType:
    """Helper function for dynamically loading python modules.
    
    This function should be used whenever a python module needs to be dynamically loaded within the framework. 
    
    For more information about python modules see https://docs.python.org/3/tutorial/modules.html. Any changes
    to the PYTHONPATH needed to find the module should be done before this function is called.
    
    Arguments:
        module_name (str): The python module to be loaded. Note that this is not a file path. It is the name of a module that can be loaded.

    Raises:
        Exception
    """

    if denote_output:
        print(f"--------- OUTPUT FROM MODULE {module_name} ----------")

    # Sometimes the module is already loaded so just reload it to capture any changes
    # Importing the initialization file should cause it to modify the state of the Workspace however is needed
    sys.stdout = override_sys_out

    

    if sys.modules.get(module_name):
        rv = importlib.reload(sys.modules.get(module_name))
    else:
        rv = importlib.import_module(module_name)

    sys.stdout = sys.__stdout__

    if denote_output:
        print(f"---------------------------------------------------")

    return rv


class override_sys_out(TextIO):
    def write(s: str):
        if len(s) > 0 and not s == "\n":
            sys.__stdout__.write(f"> {s}\n")
