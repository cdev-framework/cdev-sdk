import importlib
import os
import sys
from typing import List, Tuple, Union

from pydantic.types import FilePath
from cdev.management.base import BaseCommand

from cdev.output import ALL_BUFFERS
from ..utils import logger
import inspect


log = logger.get_cdev_logger(__name__)

DEFAULT_RESOURCE_LOCATION = os.path.join(os.path.dirname(__file__), ".." ,"resources")
COMMANDS_DIR = "commands"

def _get_module_name_from_path(fp):
    return fp.split("/")[-1][:-3]

def run_command(args):
    print(args)
    params = vars(args)

    sub_command = params.get("args")[0]


    if len(sub_command.split(".")) > 0:
        print(params)
        nested_command = sub_command.split(".")
        nested_command.append(params.get("args")[1])
        did_found_command, location = _find_command(nested_command)
        if did_found_command:
            log.debug(location)
            _start_dir = os.getcwd()
            mod_name = _get_module_name_from_path(location)
        
            if sys.modules.get(mod_name):
                #print(f"already loaded {mod_name}")
                importlib.reload(sys.modules.get(mod_name))
            
            os.chdir(os.path.dirname(location))

            mod = importlib.import_module(mod_name)
            
            for item in dir(mod):    
                if inspect.isclass(getattr(mod,item)) and issubclass(getattr(mod,item), BaseCommand) and not (getattr(mod,item) == BaseCommand):
                    # Find all the Cdev_Resources in the module and render them
                    init_obj = getattr(mod,item)()
                    _execute_command(init_obj, params.get("args"))
                    
                    
            os.chdir(_start_dir)
        else:
            print("DID NOT FIND COMMAND")

def _execute_command(command_obj, param: List[str]):
    command_obj.run_from_command_line(param)


def _find_command(command: List[str]) -> Tuple[bool, Union[str, None]]:
    """
    This command will search for the given command. Search order is:
    
    1. default included cdev resources
    2. Installed applications
    3. local project commands
    """
    ALL_LOCATIONS = [DEFAULT_RESOURCE_LOCATION]

    found_command = False
    found_starting_point = None
    for potential_starting_point in ALL_LOCATIONS:
        # See if the starting dir has the correct directory
        if not command[0] in os.listdir(potential_starting_point):
            log.debug(f"{potential_starting_point} does not contain {command[0]} -> {command}")
            continue

        # Check if that location has a commands folder
        if not COMMANDS_DIR in os.listdir(os.path.join(potential_starting_point, command[0])):
            log.debug(f"{potential_starting_point} does not contain command dir ({COMMANDS_DIR}) -> {command}")            
            continue

        if _recursive_find_command_in_dir(command[1:], os.path.join(potential_starting_point, command[0], COMMANDS_DIR)):
            found_command = True
            found_starting_point = potential_starting_point
            break

        log.debug(f"Did not find {command} in {potential_starting_point}")

    
    log.debug(f"Found command {command} starting at {found_starting_point}")
    if found_command:
        command_location = os.path.join(found_starting_point, command[0], COMMANDS_DIR, *command[1:-1], f"{command[-1]}.py" )
    else:
        command_location = None


    return (found_command, command_location)

def _recursive_find_command_in_dir(command: List[str], starting_dir: FilePath):
    """
    This is used to recursively find if a command file is in a given directory. It looks for the first arg in commands as a directory and then recursively looks further down the dir.
    If the command is a list of len == 1 then it looks for the arg as a .py file in the given directory. If command is empty return False. 
    """
    log.debug(f"{command}; {starting_dir}")
    if not command:
        return False

    if len(command) == 1:
        log.debug(os.listdir(starting_dir))
        if f"{command[0]}.py" in os.listdir(starting_dir):
            return True

        else:
            return False

    if command[0] in os.listdir(starting_dir):
        return _recursive_find_command_in_dir(command[1:], os.path.join(starting_dir, command[0]))

    else:
        return False


