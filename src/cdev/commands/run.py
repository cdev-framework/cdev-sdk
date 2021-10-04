import importlib
import os
import sys
from types import ModuleType
from typing import Container, List, Tuple, Union

from pydantic.types import FilePath, StrictBool
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

class TooManyCommandClasses(Exception):
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
        program_name, command, is_command = _find_command(sub_command)
    except NoCommandFound as e:
        print(f"Could not find command {sub_command}")
        return
    except AmbiguousCommandName as e:
        print(f"{sub_command} is ambiguous")
        return 
        


    full_mod_name = f"{program_name}.{command}" if command else program_name
 
    # sometime the module is already loaded so just reload it to capture any changes
    if sys.modules.get(full_mod_name):
        importlib.reload(sys.modules.get(full_mod_name))
    
    mod = importlib.import_module(full_mod_name)

    try:
        if is_command:
            execute_command(mod, (program_name, command, params.get("args")))
        else:
            execute_command_container(mod)
    except TooManyCommandClasses:
        print("Too mayn commands in module")
    except NoCommandFound:
        print(f"Could not find command {sub_command}")
    except Exception as e:
        raise e
    


def execute_command(mod: ModuleType, info: Tuple):
    """
    Run a BaseCommand child from the given module. The info param provides information to run the commands including params provided to the command.

    Args:
        mod (module): Loaded module that contains the command
        info tuple(program_name, command_name, params): information to run the function

    Returns:
        None

    Raises:
        TooManyCommandClasses
        NoCommandFound
    """

    # Check for the class that derives from BaseCommand... if there is more then one class then throw error (note this is a current implementation detail)
    # because it is easier if their is only one command per file so that we can use the file name as the command name
    _has_found_a_valid_command = False
    _object_name = None
    for item in dir(mod):    
        if inspect.isclass(getattr(mod,item)) and issubclass(getattr(mod,item), BaseCommand) and not (getattr(mod,item) == BaseCommand):
            if _has_found_a_valid_command:
                # TODO better exception
                log.error(f"Found too many commands in module {mod.__name__}")
                raise TooManyCommandClasses

            _has_found_a_valid_command = True
            # Find all the Cdev_Resources in the module and render them
            _object_name = item
    if _has_found_a_valid_command:
        # initalize an instance of the class
        init_obj  =  getattr(mod, _object_name)()

        _execute_command(init_obj, [info[0], info[1], *info[2]])
    else:
        log.error(f"Found no class that is a subclass of 'BaseCommand' in {mod}")
        raise NoCommandFound


def execute_command_container(mod: ModuleType):
    # Check for the class that derives from BaseCommand... if there is more then one class then throw error (note this is a current implementation detail)
    # because it is easier if their is only one command per file so that we can use the file name as the command name
    _has_found_a_valid_command = False
    _object_name = None
    for item in dir(mod):    
        if inspect.isclass(getattr(mod,item)) and issubclass(getattr(mod,item), BaseCommandContainer) and not (getattr(mod,item) == BaseCommandContainer):
            if _has_found_a_valid_command:
                # TODO better exception
                log.error(f"Found too many command containters in module {mod.__name__}")
                raise TooManyCommandClasses

            _has_found_a_valid_command = True
            # Find all the Cdev_Resources in the module and render them
            _object_name = item
    if _has_found_a_valid_command:
        # initalize an instance of the class
        init_obj  =  getattr(mod, _object_name)()

        init_obj.display_help_message()
    else:
        log.error(f"Found no class that is a subclass of 'BaseCommand' in {mod}")
        raise NoCommandFound
        


def _execute_command(command_obj, param: List[str]):
    command_obj.run_from_command_line(param)


def _find_command(command: str) -> Tuple[str, str, bool]:
    """
    Find the desired command based on the search path

    Args:
        command (str): The full command to search for. can be '.' seperated to denote search path. 

    Returns:
        tuple: location, app_name, is_command

    Raises:
        KeyError: Raises an exception.
    """

    # Command in list form
    command_list = command.split(".")

    # Create list of all directories to start searching in
    all_search_locations_list = [DEFAULT_RESOURCE_LOCATION]
    all_search_locations_list.extend(PROJECT.get_commands())
    
    if len(command_list) == 1:
        return _find_unspecified_command(command_list[0], all_search_locations_list)

    else:
        return _find_specified_command(command_list, all_search_locations_list)
    


def _find_specified_command(command_list: List[str], all_search_locations_list: List[str]) -> Tuple[str, str, bool]:
    for search_location in all_search_locations_list:
        # All start locations should have a '<commands_dir>' folder that is a valid python module
        actual_search_start = f"{search_location}.{COMMANDS_DIR}"


        # This a specified command, so it must be in the described searched path
        search_location_list = search_location.split(".")

        if not command_list[0] == search_location_list[-1]:
            # top level names do not match so don't even try recursively looking
            print(f"Top level name do not match -> {command_list}; {search_location_list}")
            continue

        # Try to find the location recursively
        did_find, location, is_command  = _recursive_find_specified_command(command_list[1:], actual_search_start)
        
        if is_command:
            if not _is_valid_command_module(f"{location}.{command_list[-1]}"):
                raise NoCommandFound
        else:
            if not  _is_valid_command_container_module(f"{location}.{command_list[-1]}"):
                raise NoCommandFound

        if did_find:
            return (location, command_list[-1], is_command)
        else:
            raise NoCommandFound



def _find_unspecified_command(command: str, all_search_locations_list: List[str]) -> Tuple[str, str, bool]:
    
    _all_potential_locations = [] # List[(location, is_command)]
    _found_at_least_one_possible = False
    for search_location in all_search_locations_list:

        # All start locations should have a '<commands_dir>' folder that is a valid python module
        actual_search_start = f"{search_location}.{COMMANDS_DIR}"

        
        if command == search_location.split(".")[-1]:
            # Command is equal to the top level package so it is a valid match to the location as a Command Container
            _all_potential_locations.extend([(actual_search_start, False)])
            _found_at_least_one_possible = True
            continue

        # recursively look through the actual start location for potential matches 
        did_find, locations = _recursive_find_unspecified_command(command, actual_search_start, [])

        if did_find:
            # The recursive search could have yielded multiple possible matches
            _found_at_least_one_possible = True
            _all_potential_locations.extend([(x,True) for x in locations])


    if not _found_at_least_one_possible:
        raise NoCommandFound
    

    valid_command_locations = []
    is_command = True
    
    
    for potential_location, is_command_local in _all_potential_locations:
        if is_command_local:
            valid_command_locations.append(potential_location) if _is_valid_command_module(f"{potential_location}.{command}") else ""
           
            is_command = is_command_local
        else:
            valid_command_locations.append(potential_location) if _is_valid_command_container_module(f"{potential_location}") else ""
            
            is_command = is_command_local
    
    #valid_command_locations = [x[0] for x in _all_potential_locations if  or ]
    if len(valid_command_locations) > 1:
        raise AmbiguousCommandName

    if len(valid_command_locations) == 0:
        raise NoCommandFound
    

    final_command = None if  not is_command else command

    return (valid_command_locations[0], final_command, is_command)


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

