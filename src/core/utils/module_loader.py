import sys
import importlib
from types import ModuleType

def import_module(module_name: str) -> ModuleType:
    """
    Helper function for dynamicall loading python modules. This function should be used whenever a python module needs to be dynamically
    loaded within the framework. For more information about python modules see https://docs.python.org/3/tutorial/modules.html. Any changes
    to the PYTHONPATH need to find the module should be done before this function is called.
    
    Arguments:
        module_name (str): The python module to be loaded. Note that this is not a file path. It is the name of a module that can be loaded.\

    Raises:
        Exception
    """


    # Sometimes the module is already loaded so just reload it to capture any changes
    # Importing the initialization file should cause it to modify the state of the Workspace however is needed
    if sys.modules.get(module_name):
        return importlib.reload(sys.modules.get(module_name))
    else:
        return importlib.import_module(module_name)
        