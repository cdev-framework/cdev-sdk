"""Utilities for working with user defined commands

[detailed description]

"""
import importlib
import inspect
import os
import sys
from typing import List, Tuple, Union

from core.constructs.commands import BaseCommand, BaseCommandContainer
from core.utils.module_loader import import_module


class AmbiguousCommandName(Exception):
    pass


class NoCommandFound(Exception):
    pass


class TooManyCommandClasses(Exception):
    pass


def find_specified_command(
    command_list: List[str], 
    all_search_locations_list: List[str]
) -> Tuple[Union[BaseCommand, BaseCommandContainer], str, str, bool]:
    
    command_list_copy = command_list.copy()

    for search_location in all_search_locations_list:
        # Search locations are denoted as python module paths, so convert the module to a path to search from
        mod = import_module(search_location)
        search_location_path = os.path.dirname(mod.__file__)
    

        did_find, is_command = _recursive_find_specified_command(
            command_list.copy(), search_location_path
        )

        if not did_find:
            continue

        full_command_module_name = f"{search_location}.{'.'.join(command_list_copy)}"

        if is_command:
            try:
                initialized_object = initialize_command_module(
                    full_command_module_name
                )
            except Exception as e:
                print(e)
                raise Exception(f"ERROR Initializing Command Module at {full_command_module_name}")

        else:
            try:
                initialized_object = initialize_command_container_module(
                    full_command_module_name
                )
            except Exception as e:
                print(e)
                raise Exception(f"ERROR Initializing Command Container Module at {search_location}.{command_list}")

        
        final_path_name =  f"{search_location}.{'.'.join(command_list_copy[:-1])}"
        command_name = command_list_copy[-1]
        return initialized_object, final_path_name, command_name, is_command


    # If we loop through all the search locations and no commands were found then throw exception
    raise NoCommandFound(f"No Command or Commands Container found for {command_list_copy}")
        

def initialize_command_module(mod_path: str) -> BaseCommand:
    
    mod = import_module(mod_path)
    # Check for the class that derives from BaseCommand... if there is more then one class then throw error (note this is a current implementation detail)
    # because it is easier if their is only one command per file so that we can use the file name as the command name
    _has_found_a_valid_command = False
    initialized_obj = None
    for item in dir(mod):
        potential_obj = getattr(mod, item)
        if (
            inspect.isclass(potential_obj)
            and issubclass(potential_obj, BaseCommand)
            and not (potential_obj == BaseCommand)
        ):
            if _has_found_a_valid_command:
                raise TooManyCommandClasses

            _has_found_a_valid_command = True

            # initialize an instance of the class
            initialized_obj = potential_obj()

    if not initialized_obj:
        raise NoCommandFound

    return initialized_obj


def initialize_command_container_module(mod_path: str) -> BaseCommandContainer:
    mod = import_module(mod_path)
    

    # Check for the class that derives from BaseCommandContainer... if there is more then one class then throw error (note this is a current implementation detail)
    # because it is easier if their is only one command per file so that we can use the file name as the command name
    _has_found_a_valid_command_container = False
    initialized_obj = None
    for item in dir(mod):
        potential_obj = getattr(mod, item)
        if (
            inspect.isclass(potential_obj)
            and issubclass(potential_obj, BaseCommandContainer)
            and not (potential_obj == BaseCommandContainer)
        ):
            if _has_found_a_valid_command_container:
                # TODO better exception
                return

            _has_found_a_valid_command_container = True

            initialized_obj = potential_obj()

    if not initialized_obj:
        raise NoCommandFound(f"Could not find command Container")

    
    return initialized_obj


def _recursive_find_specified_command(
    command_list: List[str], search_path: str
) -> Tuple[bool, bool]:
    """Return if the given command list results in a potential found command or command container

    Recursively check at each step if the next part in the command list is valid. If at the end of the 
    list return that something was found. If at any point there is a missing link then return False.

    Args:
        command_list (List[str]): List of command parts
        search_path (str): Path the search from

    Returns:
        Tuple[bool, bool]: Found, Is_Command
    """
    

    if len(command_list) == 1:
        # A location was specified and we are the final part of the command so the command must be a py file in this dir
        # of be a directory that has a command container
        if os.path.isfile(os.path.join(search_path, command_list[0]+".py")):
            return (True, True)

        if os.path.isdir(os.path.join(search_path, command_list[0])):
            if os.path.join(os.path.join(search_path, command_list[0], "__init__.py")):
                return (True, False)

        return (False, False)


    next_command_part = command_list.pop(0)

    if not next_command_part in os.listdir(search_path):
        return (False, False)

    return _recursive_find_specified_command(command_list, os.path.join(search_path, next_command_part))


