from enum import Enum
import json
import os
from typing import Any, Dict, List, Optional, TypeVar, Tuple, Callable

from pydantic import BaseModel
from pydantic.types import DirectoryPath

from core.constructs.backend import Backend_Configuration
from core.constructs.mapper import CloudMapper
from core.constructs.components import Component
from core.constructs.types import F
from core.constructs.cloud_output import Cloud_Output
from core.constructs.settings import Settings, Settings_Info

from .environment import environment_info, Environment

_GLOBAL_PROJECT = None


class Project_Info(BaseModel):
    project_name: str
    environment_infos: List[environment_info]
    default_backend_configuration: Backend_Configuration
    current_environment_name: Optional[str]


class Project_State(str, Enum):
    INFO_LOADED = "INFO_LOADED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"


###############################
##### Exceptions
###############################
class ProjectError(Exception):
    pass


class EnvironmentDoesNotExist(ProjectError):
    pass


class BackendError(ProjectError):
    pass


class FilesystemError(ProjectError):
    pass


def wrap_phases(phases: List[Project_State]) -> Callable[[F], F]:
    """
    Annotation that denotes when a function can be executed within the life cycle of a workspace. Throws excpetion if the workspace is not in the correct
    phase.
    """

    def inner_wrap(func: F) -> F:
        def wrapper_func(project: "Project", *func_posargs, **func_kwargs):

            current_state = project.get_state()
            if not current_state in phases:
                raise Exception(
                    f"Trying to call {func} while in project state {current_state} but need to be in {phases}"
                )

            else:

                return func(project, *func_posargs, **func_kwargs)

        return wrapper_func

    return inner_wrap


class Project:
    """
    Global class that defines the functionality for the Project object. The Project object is a global object that is created
    by Cdev to provide access to helpful API's for developers to use in their projects. The object is created and managed by
    the Cdev framework and follows a set of lifecycle rules (link to documentation).

    Developers can access the object in their projects by calling `Project.instance()`. When using the Project Object, developers
    should keep in mind the lifecycle rules around each API and how it fits into their project.

    """

    _settings: Settings

    @classmethod
    def instance(cls):
        """
        Method to retrieve the global instance of the Project object.
        """
        if not _GLOBAL_PROJECT:
            raise Exception("Currently No GLOBAL PROJECT OBJECT")

        return _GLOBAL_PROJECT

    @classmethod
    def set_global_instance(cls, project: "Project") -> None:
        """
        Method to set the global Project object. Should only be used to as defined in the lifecycle of the Cdev process. (documentation)
        """
        global _GLOBAL_PROJECT
        _GLOBAL_PROJECT = project

    @classmethod
    def remove_global_instance(cls, caller: "Project") -> None:
        """
        Method to reset the Global Project object. This should be the final cleanup step for a Cdev process.
        """
        global _GLOBAL_PROJECT

        if not _GLOBAL_PROJECT:
            raise Exception("Global Project is not set")

        if not _GLOBAL_PROJECT == caller:
            raise Exception("Only the current Project object can remove itself")

        _GLOBAL_PROJECT = None

    def set_name(self, name: str) -> None:
        """
        Set the name of this Project

        Args:
            name (str): name of the Project
        """
        raise NotImplementedError

    def get_name(self) -> str:
        """
        Get the name of this Project

        Returns:
            name (str)
        """
        raise NotImplementedError

    def get_state(self) -> Project_State:
        """
        Get the current lifecycle state of the Project.

        Returns:
            state (Project_State)
        """
        raise NotImplementedError

    def initialize_project(self) -> None:
        """
        Initialize the Project object so that it is ready to perform a given operation. Note that any configuration needed for the initialization
        process should be defined during the creation of the object, and set such that this function needs no input.
        """
        raise NotImplementedError

    def terminate_project(self) -> None:
        """
        Terminate the Project object as a cleanup operation after a given operation is complete. This should be the final step in the life cycle
        of an operation that need to initialize the project.
        """
        raise NotImplementedError

    def create_environment(
        self, environment_name: str, backend_configuration: Backend_Configuration = None
    ) -> None:
        """
        Create a new environment for this project.
        """
        raise NotImplementedError

    def destroy_environment(self, environment_name: str) -> None:
        """
        Destroy an environment. This function should only be called when the project is in the Initialized state, so that
        any cloud resources in the environment will be destroyed.
        """
        raise NotImplementedError

    def get_all_environment_names(self) -> List[str]:
        """
        Get all the available environments in the Project.

        Returns:
            environment_names (List[str]): environments
        """
        raise NotImplementedError

    def get_current_environment_name(self) -> str:
        """
        Get the environment name that is currently active for this Project.

        Returns:
            environment_name (str)
        """
        raise NotImplementedError

    def set_current_environment(self, environment_name: str) -> None:
        """
        Change the currently active environment for this Project. This should only be called when the Project is
        in the Uninitialized state to prevent it from being called during operations that modify an environment.

        Arguments:
            environment_name (str): The environment name to switch to

        Raises:
            EnvironmentDoesNotExist
        """
        raise NotImplementedError

    def get_environment(self, environment_name: str) -> Environment:
        """
        Get the environment object for a specified environment name. Note that the environment will be in a state
        based on when this function is called within the Cdev lifecycle.

        Arguments:
            environment_name (str): The environment name to switch to

        Raises:
            EnvironmentDoesNotExist
        """
        raise NotImplementedError

    def get_current_environment(self) -> Environment:
        """
        Get the environment object for the currently active Environment. Note that the Environment will be in a state
        based on when this function is called within the Cdev lifecycle.

        Raises:
            EnvironmentDoesNotExist
        """
        raise NotImplementedError

    ############################
    ##### Settings
    ############################
    @property
    def settings(self) -> Settings:
        raise NotImplementedError

    @settings.setter
    def settings(self, value: Settings):
        raise NotImplementedError

    def get_environment_settings_info(
        self, environment_name: str = None
    ) -> Settings_Info:
        raise NotImplementedError

    def update_environment_settings_info(
        self, new_value: Settings_Info, environment_name: str = None
    ):
        raise NotImplementedError

    #######################
    ##### Display Output
    #######################

    def display_output(self, tag: str, output: Cloud_Output) -> None:
        """Display the output from a Resource or Reference after a process has completed

        Args:
            tag: A key value to display with the output
            output: The Cloud Output to render
        """
        raise NotImplementedError

    def render_outputs(self) -> List[Tuple[str, Any]]:
        """Render the output associated with the Workspace

        Returns:
            List[Tuple[str, Any]]: The List of outputs with their associated tag

        """
        raise NotImplementedError

    #################
    ##### Mappers
    #################
    def add_mapper(self, mapper: CloudMapper) -> None:
        """
        Add a CloudMapper to the project. The order that the Mappers are added to the Project defines the precedence give when
        determining which CloudMapper to use.

        Note that this function should only be called during the `Project Initialization` part of the Cdev lifecycle.

        Arguments:
            mapper (CloudMapper): The mapper to add
        """
        raise NotImplementedError

    def add_mappers(self, mappers: List[CloudMapper]) -> None:
        """
        Add a List of CloudMappers to the project. The order that the Mappers are added to the Project defines the precedence
        give when determining which CloudMapper to use.

        Note that this function should only be called during the `Project Initialization` part of the Cdev lifecycle.

        Arguments:
            mappers (List[CloudMapper]): The mapper to add
        """
        raise NotImplementedError

    def get_mappers(self) -> List[CloudMapper]:
        """
        Return the List of CloudMappers for this Project.

        Note that this function should only be called during the `Project Initialized` part of the Cdev lifecycle.

        Returns:
            mappers (List[CloudMapper]): mappers for this Project
        """
        raise NotImplementedError

    def get_mapper_namespace(self) -> Dict[str, CloudMapper]:
        """
        Return the Dictionary that maps Resource ID's (ruuid) to the mapper that will be used to deploy the resource into the cloud.

        Note that this function should only be called during the `Project Initialized` part of the Cdev lifecycle.

        Returns:
            ruuid_to_mapper (Dict[str, CloudMapper]): Resource ID to CloudMapper
        """
        raise NotImplementedError

    #################
    ##### Commands
    #################
    def add_command(self, command_location: str):
        """
        Add a Command Location to the Project. The order that the Command is added to the Project defines the precedence
        give when searching for Commands. Command Locations should adhere to the defined form to ensure that they can be
        found within the Project.

        Note that this function should only be called during the `Project Initialization` part of the Cdev lifecycle.

        Arguments:
            command_location (Command): The command location to add
        """
        raise NotImplementedError

    def add_commands(self, command_locations: List[str]):
        """
        Add a List of Command Locations to the Project. The order that the Commands are added to the Project defines the precedence
        give when searching for a Command. Command Locations should adhere to the defined form to ensure that they can be
        found within the Project.

        Note that this function should only be called during the `Project Initialization` part of the Cdev lifecycle.

        Arguments:
            command_locations (Command): The command location to add
        """
        raise NotImplementedError

    def get_commands(self) -> List[str]:
        """
        Get the Command Locations for this Project.

        Note that this function should only be called during the `Project Initialized` part of the Cdev lifecycle.

        Returns:
            command_locations (List[str])
        """
        raise NotImplementedError

    #################
    ##### Components
    #################
    def add_component(self, component: Component) -> None:
        """
        Add a Component to the Project. Components are used to determine the desired state of the Project. They should represent
        a logical separation for the Resources in a project.

        Note that this function should only be called during the `Project Initialization` part of the Cdev lifecycle.

        Arguments:
            component (Component): Component to add
        """
        raise NotImplementedError

    def add_components(self, components: List[Component]) -> None:
        """
        Add a List of Components to the Project. Components are used to determine the desired state of the Project. They
        should represent a logical separation for the Resources in a project.

        Note that this function should only be called during the `Project Initialization` part of the Cdev lifecycle.

        Arguments:
            component (Component): Component to add
        """
        raise NotImplementedError

    def get_components(self) -> List[Component]:
        """
        Return the Components for this Project.

        Note that this function should only be called during the `Project Initialized` part of the Cdev lifecycle.

        Returns:
            components (List[Component])
        """
        raise NotImplementedError


def check_if_project_exists(base_directory: DirectoryPath) -> bool:
    """
    This function checks for an existing Cdev project at the given directory. A Cdev project is defined by the existence of a valid
    'cdev_project.json' file (can be loaded as project_info) at the location of <base_directory>/.cdev/.

    Arguments:
        base_directory: Directory to start search from
    """

    CDEV_FOLDER = ".cdev"
    CDEV_PROJECT_FILE = "cdev_project.json"

    if not os.path.isdir(base_directory):
        raise Exception(f"Given base directory is not a directory {base_directory}")

    if not os.path.isdir(os.path.join(base_directory, CDEV_FOLDER)):
        return False

    if not os.path.isfile(os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)):
        return False

    try:
        with open(
            os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE), "r"
        ) as fh:
            Project_Info(**json.load(fh))

        return True

    except Exception as e:
        return False
