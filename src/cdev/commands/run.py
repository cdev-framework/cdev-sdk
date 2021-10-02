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

class AmbiguousCommandName(Exception):
    pass

class NoCommandFound(Exception):
    pass

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

    try:
        program_name, command = _find_command(sub_command)
    except NoCommandFound as e:
        print(f"Could not find command {sub_command}")
        return
    except AmbiguousCommandName as e:
        print(f"{sub_command} is ambiguous")
        return
        

    print(program_name)
    print(command)
        

    
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


def _find_command(command: str) -> Tuple[str, str]:
    """
    Find the desired command based on the search path

    Args:
        command (str): The full command to search for. can be '.' seperated to denote search path. 

    Returns:
        tuple: location, app_name, is_command_container

    Raises:
        KeyError: Raises an exception.
    """


    command_list = command.split(".")
    all_search_locations_list = [DEFAULT_RESOURCE_LOCATION]
    all_search_locations_list.extend(PROJECT.get_commands())


    _all_potential_locations = [] # (location, is_command)
    _found_at_least_one_possible = False
    for search_location in all_search_locations_list:

        actual_search_start = f"{search_location}.{COMMANDS_DIR}"
        if len(command_list) == 1:
            print(search_location)
            if command_list[0] == search_location.split(".")[-1]:
                print(f"Top level name match -> {command_list}; {search_location}")
                _all_potential_locations.extend([(actual_search_start, False)])
                _found_at_least_one_possible = True
                continue

            did_find, locations = _recursive_find_unspecified_command(command_list[0], actual_search_start, [])
            
            if did_find:
                _found_at_least_one_possible = True
                _all_potential_locations.extend([(x,True) for x in locations])
        else:
            search_location_list = search_location.split(".")

            if not command_list[0] == search_location_list[-1]:
                print(f"Top level name do not match -> {command_list}; {search_location_list}")
                continue

            did_find, location, is_command  = _recursive_find_specified_command(command_list[1:], actual_search_start)
            
            if is_command:
                if not _is_valid_command_module(f"{location}.{command_list[-1]}"):
                    raise NoCommandFound
            else:
                if not  _is_valid_command_container_module(f"{location}.{command_list[-1]}"):
                    raise NoCommandFound

            if did_find:
                return (location, is_command), command_list[-1]
            else:
                raise NoCommandFound

    print(_all_potential_locations)
    if not _found_at_least_one_possible:
        raise NoCommandFound
    

    valid_command_locations = []
    for potential_location in _all_potential_locations:
        if potential_location[0]:
            valid_command_locations.append(potential_location) if _is_valid_command_container_module(f"{potential_location[0]}") else ""

        else:
            valid_command_locations.append(potential_location) if _is_valid_command_module(f"{potential_location[0]}.{command_list[0]}") else ""
    
    #valid_command_locations = [x[0] for x in _all_potential_locations if  or ]
    if len(valid_command_locations) > 1:
        raise AmbiguousCommandName

    if len(valid_command_locations) == 0:
        raise NoCommandFound

    return valid_command_locations[0], command_list[0]






def _is_valid_command_module(mod_path: str):
    mod = importlib.import_module(mod_path)
    
    # Check for the class that derives from BaseCommand... if there is more then one class then throw error (note this is a current implementation detail)
    # because it is easier if their is only one command per file so that we can use the file name as the command name
    _has_found_a_valid_command = False
    _object_name = None
    for item in dir(mod):    
        if inspect.isclass(getattr(mod,item)) and issubclass(getattr(mod,item), BaseCommand) and not (getattr(mod,item) == BaseCommand):
            if _has_found_a_valid_command:
                # TODO better exception
                log.error(f"Found too many commands in file {mod_path}")
                return

            _has_found_a_valid_command = True

    return _has_found_a_valid_command


def _is_valid_command_container_module(mod_path: str):
    mod = importlib.import_module(mod_path)
    
    
    # Check for the class that derives from BaseCommandContainer... if there is more then one class then throw error (note this is a current implementation detail)
    # because it is easier if their is only one command per file so that we can use the file name as the command name
    _has_found_a_valid_command_container = False
    _object_name = None
    for item in dir(mod):

        if inspect.isclass(getattr(mod,item)) and issubclass(getattr(mod,item), BaseCommandContainer) and not (getattr(mod,item) == BaseCommandContainer):
            if _has_found_a_valid_command_container:
                # TODO better exception
                log.error(f"Found too many commands in file {mod_path}")
                return

            _has_found_a_valid_command_container = True

    return _has_found_a_valid_command_container



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
                    # of be a directory that has a command container 
                    if is_dir:      
                        if os.path.isfile(os.path.join(current_location_attempt, command_list[0], "__init__.py")):
                            return (True, search_path, False)
                        else:
                            continue
                    else:
                        if potential_location[:-3] == command_list[0]:
                            #print(f"Found Command at -> {os.path.join(current_location_attempt, potential_location)}")
                            return (True, search_path, True)
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

        return (False, "", False)
                        
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

        if not os.listdir(current_location_attempt):
            return

        for potential_location in os.listdir(current_location_attempt):
            is_dir = os.path.isdir(os.path.join(current_location_attempt, potential_location))
            
            if (potential_location[-3:] == ".py" or is_dir ) and not potential_location in SKIPS:
                # A location was specified and we are still have paths to search down for the command so if this element is not a dir and if it is recursively keep searching
                if not is_dir:
                    if potential_location[:-3] == command:
                        #print(f"Found Command at -> {os.path.join(current_location_attempt, potential_location)}")
                        return (True, [search_path] )
                    else:
                        continue
                else:
                    #print(f"Recursively look in -> {os.path.join(current_location_attempt, potential_location)} for {command}")
                    did_find, locations = _recursive_find_unspecified_command(command, f"{search_path}.{potential_location}", new_locations)

                    if did_find:
                        new_locations = new_locations + locations
                        found_any_matches = True

                    
        return (found_any_matches, new_locations) 
                        
    except Exception as e:        
        log.debug(f"{search_path} did not have a file commands that was importable")
        return (False, [""])


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
