from enum import Enum
import inspect
from rich.console import Console, ConsoleOptions
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from typing import Callable, List, Dict, Any, Tuple, TypeVar, Union
from networkx.classes.digraph import DiGraph
from networkx.classes.graph import NodeView

from pydantic import BaseModel

from core.output.output_manager import OutputManager

from .resource import Resource_Change_Type, Resource_Difference, Resource_Reference, Resource_Reference_Difference
from .backend import Backend
from .mapper import CloudMapper
from .components import Component, Component_Change_Type, Component_Difference, ComponentModel


from .commands import BaseCommand, BaseCommandContainer

from ..settings import SETTINGS as cdev_settings

from ..utils.command_finder import find_specified_command, find_unspecified_command
from ..utils import module_loader, topological_helper


WORKSPACE_INFO_DIR = cdev_settings.get("ROOT_FOLDER_NAME")
WORKSPACE_INFO_FILENAME = cdev_settings.get("WORKSPACE_FILE_NAME")

_GLOBAL_WORKSPACE: "Workspace" = None

F = TypeVar("F", bound=Callable[..., Any])


class Workspace_Info(BaseModel):
    python_module: str
    python_class: str
    config: Dict

    def __init__(
        __pydantic_self__, python_module: str, python_class: str, config: Dict
    ) -> None:
        """
        Represents the data needed to create a new cdev workspace:

        Parameters:
            python_module: The name of the python module to load as the workspace
            python_class: The name of the class in the python module to initialize
            config: configuration option for the workspace

        """

        super().__init__(
            **{
                "python_module": python_module,
                "python_class": python_class,
                "config": config,
            }
        )


class Workspace_State(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"
    EXECUTING_FRONTEND = "EXECUTING_FRONTEND"
    EXECUTING_BACKEND = "EXECUTING_BACKEND"


def wrap_phase(phases: List[Workspace_State]) -> Callable[[F], F]:
    """
    Annotation that denotes when a function can be executed within the life cycle of a workspace. Throws excpetion if the workspace is not in the correct
    phase.
    """

    def inner_wrap(func: F) -> F:
        def wrapper_func(workspace: "Workspace", *func_posargs, **func_kwargs):

            current_state = workspace.get_state()
            if not current_state in phases:
                raise Exception(
                    f"Trying to call {func} while in workspace state {current_state} but need to be in {phases}"
                )

            else:
                rv = func(workspace, *func_posargs, **func_kwargs)
                return rv

        return wrapper_func

    return inner_wrap


class Workspace:
    """
    A singleton that encapsulates the configuration and high level information needed to construct the project. This singleton
    can be used within the different components to gain information about the higher level project that it is within. Once constructed,
    the object should remain a read only object to prevent components from changing configuration beyond their scope.
    """

    @classmethod
    def instance(cls):
        if not _GLOBAL_WORKSPACE:
            raise Exception("Currently No Global Workspace")

        return _GLOBAL_WORKSPACE

    @classmethod
    def set_global_instance(cls, workspace: "Workspace"):
        global _GLOBAL_WORKSPACE
        _GLOBAL_WORKSPACE = workspace

    @classmethod
    def remove_global_instance(cls, caller: "Workspace"):
        """
        Method to reset the Global Workspace object. This should be the final cleanup step for a Cdev process.
        """
        global _GLOBAL_WORKSPACE

        if not _GLOBAL_WORKSPACE:
            raise Exception("Global Workspace is not set")

        if not _GLOBAL_WORKSPACE == caller:
            raise Exception("Only the current Workspace object can remove itself")

        _GLOBAL_WORKSPACE = None

    def initialize_workspace(self, workspace_configuration: Workspace_Info):
        """
        Run the configuration needed to initialize a workspace. This should generally only be called by the Core framework itself to ensure that the
        life cycle of a workspace is correctly handled.
        """
        raise NotImplementedError

    def destroy_workspace(self):
        raise NotImplementedError

    ################
    ##### Initialized
    ################
    def get_state(self) -> Workspace_State:
        """
        Get the current lifecycle state of the Workspace.

        Returns:
            state (Workspace_State)
        """
        raise NotImplementedError

    def set_state(self, value: Workspace_State):
        """
        Set the current lifecycle state of the Workspace.

        Arguments:
            value (Workspace_State)
        """
        raise NotImplementedError

    #################
    ##### Mappers
    #################
    def add_mapper(self, mapper: CloudMapper) -> None:
        """
        Add a CloudMapper to the project. The order that the Mappers are added to the Workspace defines the precedence give when
        determining which CloudMapper to use.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            mapper (CloudMapper): The mapper to add
        """
        raise NotImplementedError

    def add_mappers(self, mappers: List[CloudMapper]) -> None:
        """
        Add a List of CloudMappers to the project. The order that the Mappers are added to the Workspace defines the precedence
        give when determining which CloudMapper to use.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            mappers (List[CloudMapper]): The mapper to add
        """
        raise NotImplementedError

    def get_mappers(self) -> List[CloudMapper]:
        """
        Return the List of CloudMappers for this Workspace.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            mappers (List[CloudMapper]): mappers for this Workspace
        """
        raise NotImplementedError

    def get_mapper_namespace(self) -> Dict[str, CloudMapper]:
        """
        Return the Dictionary that maps Resource ID's (ruuid) to the mapper that will be used to deploy the resource into the cloud.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            ruuid_to_mapper (Dict[str, CloudMapper]): Resource ID to CloudMapper
        """
        raise NotImplementedError

    #################
    ##### Commands
    #################
    def add_command(self, command_location: str):
        """
        Add a Command Location to the Workspace. The order that the Command is added to the Workspace defines the precedence
        give when searching for Commands. Command Locations should adhere to the defined form to ensure that they can be
        found within the Workspace.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            command_location (Command): The command location to add
        """
        raise NotImplementedError

    def add_commands(self, command_locations: List[str]):
        """
        Add a List of Command Locations to the Workspace. The order that the Commands are added to the Workspace defines the precedence
        give when searching for a Command. Command Locations should adhere to the defined form to ensure that they can be
        found within the Workspace.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            command_locations (Command): The command location to add
        """
        raise NotImplementedError

    def get_commands(self) -> List[str]:
        """
        Get the Command Locations for this Workspace.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            command_locations (List[str])
        """
        raise NotImplementedError

    #################
    ##### Components
    #################
    def add_component(self, component: Component):
        """
        Add a Component to the Workspace. Components are used to determine the desired state of the Workspace. They should represent
        a logical separation for the Resources in a project.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            component (Component): Component to add
        """
        raise NotImplementedError

    def add_components(self, components: List[Component]):
        """
        Add a List of Components to the Workspace. Components are used to determine the desired state of the Workspace. They
        should represent a logical separation for the Resources in a project.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            component (Component): Component to add
        """
        raise NotImplementedError

    def get_components(self) -> List[Component]:
        """
        Return the Components for this Workspace.

        Note that this function should only be called during the `Workspace Initialized` or `Executing Frontend` part of the Cdev lifecycle.

        Returns:
            components (List[Component])
        """
        raise NotImplementedError

    ################
    ##### Backend
    ################
    def get_backend(self) -> Backend:
        """
        Return the Backend that is associated with this Workspace.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            backend (Backend): Initialized Backend for the Workspace
        """
        raise NotImplementedError

    def set_backend(self, backend: Backend):
        """
        Set the Backend for the Workspace.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            backend (Backend):  Initialized Backend for the Workspace
        """
        raise NotImplementedError

    def set_resource_state_uuid(self, resource_state_uuid: str):
        """
        Set the Resource State UUID to denote the Resource State that this Workspace will execute over.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            resource_state_uuid (str): Resource State UUID from the Backend
        """
        raise NotImplementedError

    def get_resource_state_uuid(self) -> str:
        """
        Get the Resource State UUID that this Workspace is executing over.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            resource_state_uuid (str): Resource State UUID from the Backend
        """
        raise NotImplementedError

    @wrap_phase([Workspace_State.EXECUTING_FRONTEND])
    def generate_current_state(self) -> List[ComponentModel]:
        """
        Execute the components of this workspace to generate the current desired state of the resources.

        Returns:
            Current State (List[ComponentModel]): The current state generated by the components.
        """

        rv = []
        components: List[Component] = self.get_components()

        for component in components:
            rv.append(component.render())

        return rv

    @wrap_phase([Workspace_State.EXECUTING_FRONTEND])
    def create_state_differences(
        self, desired_state: List[ComponentModel], previous_state_component_names: List[str]
    ) -> Tuple[
        Component_Difference, Resource_Difference, Resource_Reference_Difference,
    ]:
        """
        Produce the differences between the desired state of the components and the current saved state

        Arguments:
            desired_state (List[ComponentModel]): The current state generated by the components.
            previous_state_component_names (List[str]): The names of the components to diff against.

        Returns:
            component_differences (List[Component_Difference]): The list of differences at the component level.
            reference_differences (List[Resource_Reference_Difference]): The list of differences for references within components.
            resource_differences (List[Resource_Difference]): The list of the difference for the resources within components.

        """

        backend = self.get_backend()
        resource_state_uuid = self.get_resource_state_uuid()

        return backend.create_differences(
            resource_state_uuid, desired_state, previous_state_component_names
        )

    @wrap_phase([Workspace_State.EXECUTING_FRONTEND])
    def sort_differences(self, differences: Tuple[Component_Difference, Resource_Reference_Difference, Resource_Difference]) -> DiGraph:
        return topological_helper.generate_sorted_resources(differences)


    @wrap_phase([Workspace_State.EXECUTING_BACKEND])
    def deploy_differences(self, differences_dag: DiGraph) -> None:

        console = Console()
        with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                TimeElapsedColumn(),
                TextColumn("{task.fields[comment]}"),
                console=console
            ) as progress:

            output_manager = OutputManager(console, progress)
            topological_helper.topological_iteration(differences_dag, self.deploy_change, output_manager=output_manager)


    @wrap_phase([Workspace_State.EXECUTING_BACKEND])
    def deploy_change(self, change: NodeView, output_manager: OutputManager) -> None:
        
        
        if isinstance(change, Resource_Difference):
        
            task_id = output_manager._progress.add_task(f"Creating backend transaction", total=3, comment='')

            transaction_token, namespace_token = self.get_backend().create_resource_change_transaction(self.get_resource_state_uuid(), change.component_name, change)


            

            ruuid = change.new_resource.ruuid if change.new_resource else change.previous_resource.ruuid

            previous_output = (
                self.get_backend().get_cloud_output_by_name(self.get_resource_state_uuid(), change.component_name, ruuid, change.previous_resource.name)
                if not change.action_type == Resource_Change_Type.CREATE else
                {}
            )

            

            

            try:
                output_manager._progress.update(task_id, advance=.5, description="Deploying on the Cloud", comment="some message")
                mapper = self.get_mapper_namespace().get(ruuid)

                
                cloud_output = mapper.deploy_resource(transaction_token, namespace_token, change, previous_output)

            
                output_manager._progress.update(task_id, completed=True, description="Completing transaction with Backend")
            
            except Exception as e:
                
                self.get_backend().fail_resource_change(self.get_resource_state_uuid(), change.component_name, change, transaction_token, {"message": "deployment error"})
                print(e)
                raise e

            try:
                self.get_backend().complete_resource_change(self.get_resource_state_uuid(), change.component_name, change, transaction_token, cloud_output)
                #output_manager.print_completed_resource_differences(change)
                output_manager._progress.update(task_id, advance=1, description="Finished deploying", comment='')

            except Exception as e:
                self.get_backend().fail_resource_change(self.get_resource_state_uuid(), change.component_name, change, transaction_token, {"message": "backend error"})
                print(e)
                raise e

        elif isinstance(change, Resource_Reference):
            pass

        elif isinstance(change, Component_Difference):
            self.get_backend().update_component(self.get_resource_state_uuid(), change)

        else:
            raise Exception(f"Trying to deploy node {change} but it is not a correct type ")


    @wrap_phase([Workspace_State.INITIALIZED])
    def execute_command(self, command: str, args: List):
        """
        Find the desired command based on the search path and execute it with the given arguments.

        Args:
            command (str): The full command to search for. can be '.' seperated to denote search path.
            args (List): The command lines arguments to pass to the command.

        Raises:
            KeyError: Raises an exception.
        """

        # Command in list form
        command_list = command.split(".")

        # Create list of all directories to start searching in
        all_search_locations_list = self.get_commands()

        if len(command_list) == 1:
            obj, program_name, command_name, is_command = find_unspecified_command(
                command_list[0], all_search_locations_list
            )

        else:
            obj, program_name, command_name, is_command = find_specified_command(
                command_list, all_search_locations_list
            )

        if is_command:
            if not isinstance(obj, BaseCommand):
                raise Exception

            try:
                args = [program_name, command_name, *args]
                obj.run_from_command_line(args)
            except Exception as e:
                raise e

        else:
            if not isinstance(obj, BaseCommandContainer):
                raise Exception

            try:
                obj.display_help_message()
            except Exception as e:
                raise e


class WorkspaceManager:
    def create_new_workspace(self, workspace_info: Workspace_Info, *posargs, **kwargs):
        """
        Create a new workspace based on the information provided.

        Args:
            workspace_info (Workspace_Info): information about the backend configuration

        Raises:
            WorkSpaceAlreadyCreated
        """
        raise NotImplementedError

    def check_if_workspace_exists(self, *posargs, **kwargs) -> bool:
        raise NotImplementedError

    def load_workspace_configuration(self, *posargs, **kwargs) -> Workspace_Info:
        raise NotImplementedError

    def load_workspace(self, *posargs, **kwargs) -> Workspace:
        raise NotImplementedError


def load_and_initialize_workspace(config: Workspace_Info):
    """
    Load and initialize the workspace from the given configuration
    """
    ws = load_workspace(config)
    ws.set_state(Workspace_State.INITIALIZING)
    initialize_workspace(ws, config.config)
    ws.set_state(Workspace_State.INITIALIZED)


def load_workspace(config: Workspace_Info) -> Workspace:
    """
    Load and initialize the workspace from the given configuration
    """
    try:
        workspace_module = module_loader.import_module(config.python_module)
    except Exception as e:
        print("Error loading workspace module")
        print(f"Error > {e}")

        raise e

    workspace_class = None
    for item in dir(workspace_module):
        potential_obj = getattr(workspace_module, item)
        if (
            inspect.isclass(potential_obj)
            and issubclass(potential_obj, Workspace)
            and item == config.python_class
        ):
            workspace_class = potential_obj
            break

    if not workspace_class:
        print(f"Could not find {config.python_class} in {config.python_module}")
        raise Exception

    try:
        # initialize the backend obj with the provided configuration values
        return workspace_class()

    except Exception as e:
        print(
            f"Could not load {workspace_class} Class from config {config.config}; {e}"
        )
        raise e


def initialize_workspace(workspace: Workspace, config: Dict):
    try:
        # initialize the backend obj with the provided configuration values
        workspace.initialize_workspace(config)

    except Exception as e:
        print(
            f"Could not initialize {workspace} Class from config {config}; {e}"
        )
        raise e
