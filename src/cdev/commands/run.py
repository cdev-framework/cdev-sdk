import importlib
import os
import sys
from typing import List, Tuple, Union

from pydantic.types import FilePath
from cdev.management.base import BaseCommand

from cdev.output import ALL_BUFFERS
from cdev.constructs import Cdev_Project
from ..utils import project, logger
import inspect


log = logger.get_cdev_logger(__name__)

DEFAULT_RESOURCE_LOCATION = os.path.join(os.path.dirname(__file__), ".." ,"resources")
COMMANDS_DIR = "commands"

PROJECT = Cdev_Project()

def _get_module_name_from_path(fp):
    return fp.split("/")[-1][:-3]

def run_command(args):
    """
    Attempts to find and run a user defined command 

    format:
    cdev run <sub_command> <args> 
    """
    # Convert namespace into dict
    params = vars(args)

    # This is the command to run... It can be a single command or a path to the command where the path is '.' delimitated
    sub_command = params.get("subcommand")

    print(sub_command)

    project.initialize_project()

    if len(sub_command.split(".")) > 1:
        nested_command = sub_command.split(".")
        did_find_command, location = _find_complex_command(nested_command)

        program_name = ".".join(nested_command[:-1])
        command_name = nested_command[-1]
    
    else:
        did_find_command, location, app_name = _find_simple_command(sub_command)
        
        program_name = app_name
        command_name = sub_command
        

    
    if did_find_command:
        # We change directory to where the command file is found so that importing works
        # note this must be understood by the user creating the command because it affects how they structure importing local modules
        _start_dir = os.getcwd()
        os.chdir(os.path.dirname(location))

        mod_name = _get_module_name_from_path(location)
        
        # sometime the module is already loaded so just reload it to capture any changes
        if sys.modules.get(mod_name):
            importlib.reload(sys.modules.get(mod_name))


        sys.path.insert(0, os.getcwd())
        mod = importlib.import_module(mod_name)
        
        # Check for the class that derives from BaseCommand... if there is more then one class then throw error (note this is a current implementation detail)
        # because it is easier if their is only one command per file so that we can use the file name as the command name
        _has_found_a_valid_command = False
        _object_name = None
        for item in dir(mod):    
            if inspect.isclass(getattr(mod,item)) and issubclass(getattr(mod,item), BaseCommand) and not (getattr(mod,item) == BaseCommand):
                if _has_found_a_valid_command:
                    # TODO better exception
                    log.error(f"Found too many commands in file {location}")
                    return

                _has_found_a_valid_command = True
                # Find all the Cdev_Resources in the module and render them
                _object_name = item

        if _has_found_a_valid_command:
            # initalize an instance of the class
            init_obj  =  getattr(mod, _object_name)()

            
            _execute_command(init_obj, [program_name, command_name, *params.get("args")])
        else:
            log.error(f"Found no class that is a subclass of 'BaseCommand' in {location}")
            return 
                
        os.chdir(_start_dir)
    else:
        # TODO Throw error
        print("DID NOT FIND COMMAND")


def _execute_command(command_obj, param: List[str]):
    command_obj.run_from_command_line(param)


def _find_simple_command(command: str) -> Tuple[bool, Union[str, None], Union[str, None] ]:
    ALL_LOCATIONS = PROJECT.get_commands()
    
    found_location = False
    for location in ALL_LOCATIONS:
        try:
            
            mod = importlib.import_module(f"{location}.commands.{command}")
            current_location_attempt = mod.__file__
        except Exception as e:
            log.debug(f"{location} did not have a file commands/{command} that was importable")
            continue
        
        found_location = True
        break

    if found_location:
        return (True, current_location_attempt, location)
    else:
        return (False, None, None)
    


def _find_complex_command(command: List[str]) -> Tuple[bool, Union[str, None]]:
    """
    This command will search for the given command. Search order is:
    
    1. default included cdev resources
    2. Installed applications
    3. local project commands
    """
    ALL_LOCATIONS = [DEFAULT_RESOURCE_LOCATION]
    ALL_LOCATIONS.append(PROJECT.INSTALLED_COMMANDS)

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


