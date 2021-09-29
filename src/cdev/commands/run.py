import importlib
import os
import sys
from typing import Container, List, Tuple, Union

from pydantic.types import FilePath
from cdev.management.base import BaseCommand, BaseCommandContainer

from cdev.output import ALL_BUFFERS
from cdev.constructs import Cdev_Project
from ..utils import project, logger
import inspect


log = logger.get_cdev_logger(__name__)

DEFAULT_RESOURCE_LOCATION = "cdev.resources.simple"
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
    
    project.initialize_project()

    did_find_command, location, app_name = _find_command(sub_command)
    
        

    
    # if did_find_command:
    #     # We change directory to where the command file is found so that importing works
    #     # note this must be understood by the user creating the command because it affects how they structure importing local modules
    #     _start_dir = os.getcwd()
    #     os.chdir(os.path.dirname(location))

    #     mod_name = _get_module_name_from_path(location)
        
    #     # sometime the module is already loaded so just reload it to capture any changes
    #     if sys.modules.get(mod_name):
    #         importlib.reload(sys.modules.get(mod_name))


    #     sys.path.insert(0, os.getcwd())
    #     mod = importlib.import_module(mod_name)
        
    #     # Check for the class that derives from BaseCommand... if there is more then one class then throw error (note this is a current implementation detail)
    #     # because it is easier if their is only one command per file so that we can use the file name as the command name
    #     _has_found_a_valid_command = False
    #     _object_name = None
    #     for item in dir(mod):    
    #         if inspect.isclass(getattr(mod,item)) and issubclass(getattr(mod,item), BaseCommand) and not (getattr(mod,item) == BaseCommand):
    #             if _has_found_a_valid_command:
    #                 # TODO better exception
    #                 log.error(f"Found too many commands in file {location}")
    #                 return

    #             _has_found_a_valid_command = True
    #             # Find all the Cdev_Resources in the module and render them
    #             _object_name = item

    #     if _has_found_a_valid_command:
    #         # initalize an instance of the class
    #         init_obj  =  getattr(mod, _object_name)()

            
    #         _execute_command(init_obj, [program_name, command_name, *params.get("args")])
    #     else:
    #         log.error(f"Found no class that is a subclass of 'BaseCommand' in {location}")
    #         return 
                
    #     os.chdir(_start_dir)
    # else:
    #     # TODO Throw error
    #     print("DID NOT FIND COMMAND")


def _execute_command(command_obj, param: List[str]):
    command_obj.run_from_command_line(param)


def _find_command(command: str) -> Tuple[bool, Union[str, None], Union[str, None] ]:
    """
    Find the desired command based on the search path

    Args:
        command (str): The full command to search for. can be '.' seperated to denote search path. 

    Returns:
        tuple: did_find_command, location, app_name 

    Raises:
        KeyError: Raises an exception.
    """


    command_list = command.split(".")
    all_search_locations_list = [DEFAULT_RESOURCE_LOCATION]
    all_search_locations_list.extend(PROJECT.get_commands())

    print(all_search_locations_list)
    for search_location in all_search_locations_list:
        print("-----------------")
        actual_search_start = f"{search_location}.{COMMANDS_DIR}"
        if len(command_list) == 1:
            did_find, locations = _recursive_find_unspecified_command(command_list[0], actual_search_start, [])
            print(did_find, locations)
        else:

            search_location_list = search_location.split(".")

            if not command_list[0] == search_location_list[-1]:
                print(f"Top level name do not match -> {command_list}; {search_location_list}")
                continue

            did_find, file_location = _recursive_find_specified_command(command_list[1:], actual_search_start)
            print(did_find, file_location)

    pass


def _recursive_find_specified_command(command_list: List[str], search_path: str) -> Tuple[bool, Union[str, None]]:
    SKIPS = set(["__init__.py", "__pycache__"])
    try: 

        mod = importlib.import_module(search_path)

        current_location_attempt = os.path.dirname(mod.__file__)


        for potential_location in os.listdir(current_location_attempt):
            is_dir = os.path.isdir(os.path.join(current_location_attempt, potential_location))
            if (potential_location[-3:] == ".py" or is_dir ) and not potential_location in SKIPS:
            
                if len(command_list) == 1:
                    # A location was specified and we are the final part of the command so the command must be a py file in this dir
                    if is_dir:      
                        continue
                    else:
                        if potential_location[:-3] == command_list[0]:
                            #print(f"Found Command at -> {os.path.join(current_location_attempt, potential_location)}")
                            return (True, os.path.join(current_location_attempt, potential_location) )
                        else:
                            continue

                else:
                    # A location was specified and we are still have paths to search down for the command so if this element is not a dir and if it is recursively keep searching
                    if not is_dir:
                        continue
                    else:
                        if command_list[0] == potential_location:
                            #print(f"Recursively look in -> {os.path.join(current_location_attempt, potential_location)} for {command_list[1:]}")
                            return _recursive_find_specified_command(command_list[1:], f"{search_path}.{potential_location}")
                        else:
                            continue

        return (False, "")
                        
    except Exception as e:
        print(f"Could not do {search_path}")
        print(e)
        #log.debug(f"{search_path} did not have a file commands that was importable")
        #return Tuple(False, "")


def _recursive_find_unspecified_command(command: str, search_path: str, found_locations: List):
    SKIPS = set(["__init__.py", "__pycache__"])


    try: 
        mod = importlib.import_module(search_path)
        current_location_attempt = os.path.dirname(mod.__file__)

        new_locations = found_locations
        found_any_matches = False
        for potential_location in os.listdir(current_location_attempt):
            is_dir = os.path.isdir(os.path.join(current_location_attempt, potential_location))
            
            if (potential_location[-3:] == ".py" or is_dir ) and not potential_location in SKIPS:
                # A location was specified and we are still have paths to search down for the command so if this element is not a dir and if it is recursively keep searching
                if not is_dir:
                    if potential_location[:-3] == command:
                        print(f"Found Command at -> {os.path.join(current_location_attempt, potential_location)}")
                        return (True, [os.path.join(current_location_attempt, potential_location)] )
                    else:
                        continue
                else:
                    print(f"Recursively look in -> {os.path.join(current_location_attempt, potential_location)} for {command}")
                    did_find, locations = _recursive_find_unspecified_command(command, f"{search_path}.{potential_location}", new_locations)

                    if did_find:
                        new_locations = new_locations + locations
                        found_any_matches = True

                    
        return (found_any_matches, new_locations) 
                        
    except Exception as e:
        print(f"Could not do {search_path}")
        print(e)
        #log.debug(f"{search_path} did not have a file commands that was importable")
        #return Tuple(False, "")


def _get_command_container_info(potential_location):
    try: 
        mod = importlib.import_module(potential_location)
        
        # Check for the class that derives from BaseCommandCommand... if there is more then one class then throw error (note this is a current implementation detail)
        _has_found_a_valid_command_container = False
        _object_name = None
        for item in dir(mod):    
            if inspect.isclass(getattr(mod,item)) and issubclass(getattr(mod,item), BaseCommandCommand) and not (getattr(mod,item) == BaseCommandCommand):
                if _has_found_a_valid_command_container:
                    # TODO better exception
                    log.error(f"Found too many command containers in mod {mod}")
                    return

                _has_found_a_valid_command_container = True
                # Find all the Cdev_Resources in the module and render them
                _object_name = item

        if _has_found_a_valid_command_container:
            # initalize an instance of the class
            init_obj  =  getattr(mod, _object_name)()

        current_location_attempt = mod.__file__


    except Exception as e:
        log.debug(f"{potential_location} did not have a file command container that was valid")
        print(e)
        




def _find_simple_command(command: str) -> Tuple[bool, Union[str, None], Union[str, None] ]:
    ALL_LOCATIONS = PROJECT.get_commands()
    
    found_location = False
    for location in ALL_LOCATIONS:
        try:
            
            mod = importlib.import_module(f"{location}.commands.{command}")
            current_location_attempt = mod.__file__
        except Exception as e:
            log.debug(f"{location} did not have a file commands/{command} that was importable")
            print(e)
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
    ALL_LOCATIONS.append(PROJECT.get_commands())

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


