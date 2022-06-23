"""
Utilities to help standardize how the framework dynamically imports code
"""
from dataclasses import dataclass, field
import sys
import importlib
from types import ModuleType
from typing import TextIO, List
import inspect


from core.utils.exceptions import cdev_core_error


###############################
##### Exceptions
###############################


@dataclass
class ImportModuleError(cdev_core_error):
    help_message: str = """
        This is a helper function used by Cdev. This error should have been wrapped by the high level components,
        and they should have provided a more informative help message.
        """
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class ImportClassError(ImportModuleError):
    help_message: str = """
        This is a helper function used by Cdev. This error should have been wrapped by the high level components,
        and they should have provided a more informative help message.
        """
    help_resources: List[str] = field(default_factory=lambda: [])


###############################
##### API
###############################


def import_module(
    module_name: str, denote_output: bool = False, override_stdout: bool = True
) -> ModuleType:
    """Helper function for dynamically loading python modules.

    This function should be used whenever a python module needs to be dynamically loaded within the framework.

    For more information about python modules see https://docs.python.org/3/tutorial/modules.html. Any changes
    to the PYTHONPATH needed to find the module should be done before this function is called.

    Args:
        module_name (str): The python module to be loaded. Note that this is not a file path. It is the name of a module that can be loaded.

    Raises:
        ImportModuleError
    """

    if denote_output:
        print(f"--------- OUTPUT FROM MODULE {module_name} ----------")

    # Sometimes the module is already loaded so just reload it to capture any changes
    # Importing the initialization file should cause it to modify the state of the Workspace however is needed

    if override_stdout:
        sys.stdout = override_sys_out

    try:
        if sys.modules.get(module_name):
            rv = importlib.reload(sys.modules.get(module_name))
        else:
            rv = importlib.import_module(module_name)
    except Exception as e:
        raise ImportModuleError(error_message=f"Could Not Import {module_name} -> {e}")

    finally:
        if override_stdout:
            sys.stdout = sys.__stdout__

    if denote_output:
        print(f"---------------------------------------------------")

    return rv


def import_class(module_name: str, class_name: str) -> type:
    """Helper function for loading a specific class from a module

    Import the given module name and then search through all the objects in the module
    for a class with a matching name. Return the `class` if found.

    Args:
        module_name (str): module name
        class_name (str): class name

    Returns:
        type: the class

    Raises:
        ImportModuleError
        ImportClassError
    """
    mod = import_module(module_name)

    for item_name in dir(mod):

        if not item_name == class_name:
            continue

        potential_obj = getattr(mod, item_name)
        if inspect.isclass(potential_obj):
            return potential_obj

    raise ImportClassError(
        error_message=f"Could not find class '{class_name}' in the loaded module '{module_name}'"
    )


class override_sys_out(TextIO):

    encoding = sys.__stdout__.encoding

    def write(s: str) -> None:
        if len(s) > 0 and not s == "\n":
            sys.__stdout__.write(f"> {s}\n")
