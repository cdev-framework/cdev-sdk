"""Utilities for working with user defined commands

[detailed description]

"""


import importlib
import inspect
import os
import sys
from typing import List, Tuple, Union

from core.constructs.commands import BaseCommand, BaseCommandContainer


from core.utils import logger


log = logger.get_cdev_logger(__name__)


COMMANDS_DIR = "commands"


class AmbiguousCommandName(Exception):
    pass


class NoCommandFound(Exception):
    pass


class TooManyCommandClasses(Exception):
    pass


def find_specified_command(
    command_list: List[str], all_search_locations_list: List[str]
) -> Tuple[Union[BaseCommand, BaseCommandContainer], str, str, bool]:
    for search_location in all_search_locations_list:
        # All start locations should have a '<commands_dir>' folder that is a valid python module
        actual_search_start = f"{search_location}.{COMMANDS_DIR}"

        # This a specified command, so it must be in the described searched path
        search_location_list = search_location.split(".")

        if not command_list[0] == search_location_list[-1]:
            # top level names do not match so don't even try recursively looking
            print(
                f"Top level name do not match -> {command_list}; {search_location_list}"
            )
            continue

        # Try to find the location recursively
        did_find, location, is_command = _recursive_find_specified_command(
            command_list[1:], actual_search_start
        )

        if is_command:
            try:
                initialized_object = initialize_command_module(
                    f"{location}.{command_list[-1]}"
                )
            except Exception as e:
                print(e)
                print("ERROR1")
                return

        else:
            try:
                print(f"calling with {location}; {command_list}")
                initialized_object = initialize_command_container_module(
                    f"{location}.{command_list[-1]}"
                )
            except Exception as e:
                print(e)
                print("ERROR2")
                return

        if did_find:
            return initialized_object, location, command_list[-1], is_command
        else:
            raise NoCommandFound


def find_unspecified_command(
    command: str, all_search_locations_list: List[str]
) -> Tuple[Union[BaseCommand, BaseCommandContainer], str, str, bool]:

    _all_potential_locations = []  # List[(location, is_command)]
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
        did_find, locations = _recursive_find_unspecified_command(
            command, actual_search_start, []
        )

        if did_find:
            # The recursive search could have yielded multiple possible matches
            _found_at_least_one_possible = True
            _all_potential_locations.extend([(x, True) for x in locations])

    if not _found_at_least_one_possible:
        print("ERROR3")
        raise NoCommandFound

    valid_command_locations = []
    is_command = True

    potential_objects = []
    for potential_location, is_command_local in _all_potential_locations:
        if is_command_local:
            try:
                potential_objects.append(
                    initialize_command_container_module(
                        f"{potential_location}.{command}"
                    )
                )
                valid_command_locations.append(potential_location)
            except Exception as e:
                log.debug(e)
                print("ERROR4")
                continue

            is_command = is_command_local
        else:
            try:
                potential_objects.append(
                    initialize_command_container_module(f"{potential_location}")
                )
                valid_command_locations.append(potential_location)
            except Exception as e:
                log.debug(e)
                print("ERROR5")
                continue

            is_command = is_command_local

    if len(potential_objects) > 1:
        print("ERROR6")
        raise AmbiguousCommandName

    if len(potential_objects) == 0:
        print("ERROR7")
        raise NoCommandFound

    final_command = None if not is_command else command

    return potential_objects[0], valid_command_locations[0], final_command, is_command


def initialize_command_module(mod_path: str) -> BaseCommand:
    # sometime the module is already loaded so just reload it to capture any changes
    if sys.modules.get(mod_path):
        importlib.reload(sys.modules.get(mod_path))

    mod = importlib.import_module(mod_path)

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
                log.error(f"Found too many commands in file {mod_path}")
                raise TooManyCommandClasses

            _has_found_a_valid_command = True

            # initialize an instance of the class
            initialized_obj = potential_obj()

    if not initialized_obj:
        raise NoCommandFound

    return initialized_obj


def initialize_command_container_module(mod_path: str) -> BaseCommandContainer:
    mod = importlib.import_module(mod_path)
    

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
                log.error(f"Found too many commands in file {mod_path}")
                return

            _has_found_a_valid_command_container = True

            initialized_obj = potential_obj()

    if not initialized_obj:
        raise NoCommandFound(f"Could not find command Container")

    print(f"final rv {initialized_obj}")
    return initialized_obj


def _recursive_find_specified_command(
    command_list: List[str], search_path: str
) -> Tuple[bool, Union[str, None]]:
    SKIPS = set(["__init__.py", "__pycache__"])
    try:

        mod = importlib.import_module(search_path)

        current_location_attempt = os.path.dirname(mod.__file__)

        for potential_location in os.listdir(current_location_attempt):
            is_dir = os.path.isdir(
                os.path.join(current_location_attempt, potential_location)
            )
            if (
                potential_location[-3:] == ".py" or is_dir
            ) and not potential_location in SKIPS:

                if len(command_list) == 1:
                    # A location was specified and we are the final part of the command so the command must be a py file in this dir
                    # of be a directory that has a command container
                    if is_dir:
                        if os.path.isfile(
                            os.path.join(
                                current_location_attempt, command_list[0], "__init__.py"
                            )
                        ):
                            return (True, search_path, False)
                        else:
                            continue
                    else:
                        if potential_location[:-3] == command_list[0]:
                            # print(f"Found Command at -> {os.path.join(current_location_attempt, potential_location)}")
                            return (True, search_path, True)
                        else:
                            continue

                else:
                    # A location was specified and we are still have paths to search down for the command so if this element is not a dir and if it is recursively keep searching
                    if not is_dir:
                        continue
                    else:
                        if command_list[0] == potential_location:
                            # print(f"Recursively look in -> {os.path.join(current_location_attempt, potential_location)} for {command_list[1:]}")
                            return _recursive_find_specified_command(
                                command_list[1:], f"{search_path}.{potential_location}"
                            )
                        else:
                            continue

        return (False, "", False)

    except Exception as e:
        print(f"Could not do {search_path}")
        print(e)
        # log.debug(f"{search_path} did not have a file commands that was importable")
        # return Tuple(False, "")


def _recursive_find_unspecified_command(
    command: str, search_path: str, found_locations: List
):
    SKIPS = set(["__init__.py", "__pycache__"])

    try:
        mod = importlib.import_module(search_path)
        current_location_attempt = os.path.dirname(mod.__file__)

        new_locations = found_locations
        found_any_matches = False

        if not os.listdir(current_location_attempt):
            return

        for potential_location in os.listdir(current_location_attempt):
            is_dir = os.path.isdir(
                os.path.join(current_location_attempt, potential_location)
            )

            if (
                potential_location[-3:] == ".py" or is_dir
            ) and not potential_location in SKIPS:
                # A location was specified and we are still have paths to search down for the command so if this element is not a dir and if it is recursively keep searching
                if not is_dir:
                    if potential_location[:-3] == command:
                        # print(f"Found Command at -> {os.path.join(current_location_attempt, potential_location)}")
                        return (True, [search_path])
                    else:
                        continue
                else:
                    # print(f"Recursively look in -> {os.path.join(current_location_attempt, potential_location)} for {command}")
                    did_find, locations = _recursive_find_unspecified_command(
                        command, f"{search_path}.{potential_location}", new_locations
                    )

                    if did_find:
                        new_locations = new_locations + locations
                        found_any_matches = True

        return (found_any_matches, new_locations)

    except Exception as e:
        log.debug(f"{search_path} did not have a file commands that was importable")
        return (False, [""])
