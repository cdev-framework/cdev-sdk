"""Construct that represents the collection of other primitives


"""
from dataclasses import dataclass, field
from enum import Enum
import inspect
from typing import Callable, List, Dict, Any, Tuple, Optional

from networkx.algorithms.dag import topological_sort
from networkx.classes.digraph import DiGraph
from networkx.classes.graph import NodeView

from pydantic import BaseModel

from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    SpinnerColumn,
)

from core.constructs.models import frozendict
from core.constructs.output_manager import OutputManager, OutputTask

from core.constructs.resource import (
    Resource_Change_Type,
    Resource_Difference,
    Resource_Reference_Difference,
    Resource_Reference_Change_Type,
    TaggableResourceModel,
)
from core.constructs.backend import (
    Backend,
    Backend_Configuration,
    BackendError,
    load_backend,
)
from core.constructs.mapper import CloudMapper
from core.constructs.components import (
    Component,
    Component_Difference,
    ComponentModel,
)
from core.constructs.commands import BaseCommand, BaseCommandContainer
from core.constructs.cloud_output import (
    Cloud_Output,
    evaluate_dynamic_output,
    cloud_output_dynamic_model,
)
from core.constructs.settings import (
    Settings_Info,
    Settings,
    initialize_settings,
    SettingsError,
)


from core.utils.command_finder import find_specified_command
from core.utils import module_loader, topological_helper
from core.utils.logger import log
from core.utils.exceptions import cdev_core_error

from core.constructs.types import F


_GLOBAL_WORKSPACE: "Workspace" = None

###############################
##### Exceptions
###############################


@dataclass
class WorkspaceInitializationError(cdev_core_error):
    help_message: str = (
        "   Commands can not be issued until the Workspace error has been resolved."
    )
    help_resources: List[str] = field(default_factory=lambda: [])


@dataclass
class WorkspaceInfoError(cdev_core_error):
    help_message: str = (
        "   Commands can not be issued until the Workspace error has been resolved."
    )
    help_resources: List[str] = field(default_factory=lambda: [])


###############################
##### Classes
###############################


class Workspace_Info(BaseModel):
    python_module: str
    python_class: str
    settings_info: Settings_Info
    backend_info: Backend_Configuration
    resource_state_uuid: str
    initialization_modules: Optional[List[str]]
    config: Optional[Dict]

    def __init__(
        __pydantic_self__,
        python_module: str,
        python_class: str,
        settings_info: Settings_Info,
        backend_info: Backend_Configuration,
        resource_state_uuid: str,
        initialization_modules: Optional[List[str]] = [],
        config: Optional[Dict] = {},
    ) -> None:
        """
        Represents the data needed to create a new cdev workspace:

        Args:
            python_module (str): The name of the python module to load as the workspace
            python_class (str): The name of the class in the python module to initialize
            settings_info (Settings_Info): Information to load settings of the `Workspace`
            backend_info (Backend_Configuration): Configuration information for the `Backend`
            resource_state_uuid (str): The `Backend` resource state uuid this `Workspace` will execute against
            initialization_modules (Optional[List[str]]): List of Python modules to dynamically import to initialize `Workspace`
            config (Optional[Dict]): configuration option for the workspace

        """

        super().__init__(
            **{
                "python_module": python_module,
                "python_class": python_class,
                "settings_info": settings_info,
                "backend_info": backend_info,
                "resource_state_uuid": resource_state_uuid,
                "initialization_modules": initialization_modules,
                "config": config,
            }
        )


class Workspace_State(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"
    EXECUTING_FRONTEND = "EXECUTING_FRONTEND"
    EXECUTING_BACKEND = "EXECUTING_BACKEND"


###############################
##### Api
###############################


def wrap_phase(phases: List[Workspace_State]) -> Callable[[F], F]:
    """
    Annotation that denotes when a function can be executed within the life cycle of a workspace.
    Throws exception if the workspace is not in the correct phase.
    """

    def inner_wrap(func: F) -> F:
        def wrapper_func(workspace: "Workspace", *func_posargs, **func_kwargs):

            current_state = workspace.get_state()
            if current_state not in phases:
                raise Exception(
                    f"Trying to call {func} while in workspace state {current_state} but need to be in {phases}"
                )

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

    _settings: Settings = None
    _resource_state_uuid: str = None

    @classmethod
    def instance(cls) -> "Workspace":
        """Get the Global instance variable to a given Workspace

        Returns:
            Workspace
        """
        if not _GLOBAL_WORKSPACE:
            raise Exception("Currently No Global Workspace")

        return _GLOBAL_WORKSPACE

    @classmethod
    def set_global_instance(cls, workspace: "Workspace") -> None:
        """Set the Global instance variable to a given Workspace

        Args:
            caller (Workspace)
        """
        global _GLOBAL_WORKSPACE
        _GLOBAL_WORKSPACE = workspace

    @classmethod
    def remove_global_instance(cls, caller: "Workspace") -> None:
        """Method to reset the Global Workspace object. This should be the final cleanup step for a Cdev process.

        Args:
            caller (Workspace)
        """
        global _GLOBAL_WORKSPACE

        if not _GLOBAL_WORKSPACE:
            raise Exception("Global Workspace is not set")

        if not _GLOBAL_WORKSPACE == caller:
            raise Exception("Only the current Workspace object can remove itself")

        _GLOBAL_WORKSPACE = None

    def initialize_workspace(
        self,
        settings_info: Settings_Info,
        backend_info: Backend_Configuration,
        resource_state_uuid: str,
        initialization_modules: Optional[List[str]] = [],
        configuration: Dict = {},
    ) -> None:
        """Run the configuration needed to initialize a workspace. This should generally only be called by the Core framework itself to ensure that the
        life cycle of a workspace is correctly handled.

        Args:
            settings_info (Settings_Info): Information to load the `Workspace` settings
            backend_info (Backend_Configuration): information to connect to the `Backend`
            resource_state_uuid (str): resource state to execute commands over
            configuration (Dict): additional configuration
        """
        try:
            initialized_backend = load_backend(backend_info)
        except BackendError as e:
            raise WorkspaceInitializationError(
                error_message=f"""Error initializing backend for the workspace ->
                {e.error_message}""",
                help_message=e.help_message,
                help_resources=e.help_resources,
            )

        self.set_backend(initialized_backend)

        top_level_resource_states = initialized_backend.get_top_level_resource_states()

        if resource_state_uuid not in set([x.uuid for x in top_level_resource_states]):
            raise WorkspaceInitializationError(
                error_message=f"{resource_state_uuid} not in loaded backend resource states: ({top_level_resource_states})"
            )

        self.set_resource_state_uuid(resource_state_uuid)

        try:
            initialized_settings = initialize_settings(settings_info)
        except SettingsError as e:
            raise WorkspaceInitializationError(
                error_message=f"""Error initializing settings for the workspace ->
                {e.error_message}""",
                help_message=e.help_message,
                help_resources=e.help_resources,
            )
        except Exception as e:
            raise WorkspaceInitializationError(
                error_message=f"Error initializing settings for the workspace -> {e}"
            )

        self.settings = initialized_settings

        if initialization_modules:
            for initialize_module in initialization_modules:
                try:
                    module_loader.import_module(initialize_module)
                except module_loader.ImportModuleError as e:
                    raise WorkspaceInitializationError(
                        error_message=f"""Error loading '{initialize_module}' to initial the workspace. The following exception occurred:
                        {e.error_message}
                        """
                    )

    def destroy_workspace(self) -> None:
        """Tear down the current Workspace

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    ############################
    ##### Settings
    ############################

    @property
    def settings(self) -> Settings:
        """Get settings object

        Returns:
            Settings
        """
        return self._settings

    @settings.setter
    def settings(self, value: Settings) -> None:
        """Set settings object"""
        self._settings = value

    ############################
    ##### Initialized
    ############################
    def get_state(self) -> Workspace_State:
        """Get the current lifecycle state of the Workspace.

        Returns:
            state (Workspace_State)
        """
        raise NotImplementedError

    def set_state(self, value: Workspace_State) -> None:
        """Set the current lifecycle state of the Workspace.

        Args:
            value (Workspace_State)
        """
        raise NotImplementedError

    #################
    ##### Mappers
    #################
    def add_mapper(self, mapper: CloudMapper) -> None:
        """Add a CloudMapper to the project. The order that the Mappers are added to the Workspace defines the precedence give when
        determining which CloudMapper to use.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Args:
            mapper (CloudMapper): The mapper to add
        """
        raise NotImplementedError

    def add_mappers(self, mappers: List[CloudMapper]) -> None:
        """Add a List of CloudMappers to the project. The order that the Mappers are added to the Workspace defines the precedence
        give when determining which CloudMapper to use.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Args:
            mappers (List[CloudMapper]): The mapper to add
        """
        raise NotImplementedError

    def get_mappers(self) -> List[CloudMapper]:
        """Return the List of CloudMappers for this Workspace.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            mappers (List[CloudMapper]): mappers for this Workspace
        """
        raise NotImplementedError

    def get_mapper_namespace(self) -> Dict[str, CloudMapper]:
        """Return the Dictionary that maps Resource ID's (ruuid) to the mapper that will be used to deploy the resource into the cloud.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            ruuid_to_mapper (Dict[str, CloudMapper]): Resource ID to CloudMapper
        """
        raise NotImplementedError

    #################
    ##### Commands
    #################
    def add_command(self, command_location: str) -> None:
        """Add a Command Location to the Workspace. The order that the Command is added to the Workspace defines the precedence
        give when searching for Commands. Command Locations should adhere to the defined form to ensure that they can be
        found within the Workspace.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Args:
            command_location (Command): The command location to add
        """
        raise NotImplementedError

    def add_commands(self, command_locations: List[str]) -> None:
        """Add a List of Command Locations to the Workspace. The order that the Commands are added to the Workspace defines the precedence
        give when searching for a Command. Command Locations should adhere to the defined form to ensure that they can be
        found within the Workspace.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Args:
            command_locations (Command): The command location to add
        """
        raise NotImplementedError

    def get_commands(self) -> List[str]:
        """Get the Command Locations for this Workspace.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            command_locations (List[str])
        """
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

    def clear_output(self) -> None:
        raise NotImplementedError

    #######################
    ##### Components
    #######################
    def add_component(self, component: Component) -> None:
        """Add a Component to the Workspace. Components are used to determine the desired state of the Workspace. They should represent
        a logical separation for the Resources in a project.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            component (Component): Component to add
        """
        raise NotImplementedError

    def add_components(self, components: List[Component]) -> None:
        """Add a List of Components to the Workspace. Components are used to determine the desired state of the Workspace. They
        should represent a logical separation for the Resources in a project.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            components (Component): Component to add
        """
        raise NotImplementedError

    def get_components(self) -> List[Component]:
        """Return the Components for this Workspace.

        Note that this function should only be called during the `Workspace Initialized` or `Executing Frontend` part of the Cdev lifecycle.

        Returns:
            components (List[Component])
        """
        raise NotImplementedError

    ################
    ##### Backend
    ################
    def get_backend(self) -> Backend:
        """Return the Backend that is associated with this Workspace.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            backend (Backend): Initialized Backend for the Workspace
        """
        raise NotImplementedError

    def set_backend(self, backend: Backend) -> None:
        """Set the Backend for the Workspace.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            backend (Backend):  Initialized Backend for the Workspace
        """
        raise NotImplementedError

    def set_resource_state_uuid(self, resource_state_uuid: str) -> None:
        """Set the Resource State UUID to denote the Resource State that this Workspace will execute over.
        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.
        Arguments:
            resource_state_uuid (str): Resource State UUID from the Backend
        """
        raise NotImplementedError

    def get_resource_state_uuid(self) -> str:
        """Get the Resource State UUID that this Workspace is executing over.
        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.
        Returns:
            resource_state_uuid (str): Resource State UUID from the Backend
        """
        raise NotImplementedError

    @wrap_phase([Workspace_State.EXECUTING_FRONTEND])
    def generate_current_state(self) -> List[ComponentModel]:
        """Execute the components of this workspace to generate the current desired state of the resources.

        Returns:
            Current State (List[ComponentModel]): The current state generated by the components.
        """

        rv = [component.render() for component in self.get_components()]
        return rv

    @wrap_phase([Workspace_State.EXECUTING_FRONTEND])
    def create_state_differences(
        self,
        desired_state: List[ComponentModel],
        previous_state_component_names: List[str],
    ) -> Tuple[
        List[Component_Difference],
        List[Resource_Difference],
        List[Resource_Reference_Difference],
    ]:
        """Produce the differences between the desired state of the components and the current saved state

        Args:
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
    def sort_differences(
        self,
        differences: Tuple[
            List[Component_Difference],
            List[Resource_Reference_Difference],
            List[Resource_Difference],
        ],
    ) -> DiGraph:
        """Given the sets of differences, sort them into a topological deployment order based on dependencies between resource outputs

        Args:
            differences (Tuple[ List[Component_Difference], List[Resource_Reference_Difference], List[Resource_Difference], ])

        Returns:
            DiGraph
        """
        return topological_helper.generate_sorted_resources(differences)

    @wrap_phase([Workspace_State.EXECUTING_BACKEND])
    def deploy_differences(self, differences_dag: DiGraph) -> None:
        """Given the sets of differences, sort them into a topological deployment order based on dependencies between resource outputs

        Args:
            differences (Tuple[ List[Component_Difference], List[Resource_Reference_Difference], List[Resource_Difference], ])

        Returns:
            DiGraph
        """
        console = Console()
        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(finished_style="white"),
            TimeElapsedColumn(),
            TextColumn("{task.fields[comment]}"),
            console=console,
        ) as progress:
            output_manager = OutputManager(console, progress)

            all_nodes_sorted: List[NodeView] = [
                x for x in topological_sort(differences_dag)
            ]

            # There seems to be some bug in Rich that causes a deadlock when creating a bunch of Tasks in a row.
            # The problem seems to be around it refreshing after creating each task, so to avoid this problem,
            # we are disabling the console while the task are created. Then turn the console back on when they
            # are created.
            # TODO: Recreate problem in isolated environment, and submit bug report.
            output_manager._progress.disable = True

            node_to_task = {
                x: output_manager.create_task(
                    output_manager.create_output_description(x),
                    start=False,
                    total=10,
                    comment="Waiting",
                )
                for x in all_nodes_sorted
            }

            # Re-enable to console to update
            output_manager._progress.disable = False

            topological_helper.topological_iteration(
                differences_dag,
                self.wrap_output_deploy_change(node_to_task),
                failed_parent_handler=self.wrap_output_failed_child(node_to_task),
            )

    @wrap_phase([Workspace_State.EXECUTING_BACKEND])
    def wrap_output_failed_child(self, tasks: Dict[NodeView, OutputTask]):
        """Wrapped function that fails any resource that has a failed parent

        Args:
            tasks (Dict[NodeView, OutputTask])
        """

        def mark_failure_by_parent(change: NodeView) -> None:
            output_task = tasks.get(change)
            output_task.update(
                advance=10,
                comment="Failed because parent resource failed to deploy :cross_mark:",
            )

        return mark_failure_by_parent

    @wrap_phase([Workspace_State.EXECUTING_BACKEND])
    def wrap_output_deploy_change(self, tasks: Dict[NodeView, OutputTask]):
        """Wrapped function callers mapper and updates backend

        Args:
            tasks (Dict[NodeView, OutputTask])
        """

        def deploy_change(change: NodeView) -> None:
            output_task = tasks.get(change)
            output_task.start_task()

            if isinstance(change, Resource_Difference):
                # Step 1 is to register a transaction with the backend

                try:
                    (
                        transaction_token,
                        namespace_token,
                    ) = self.get_backend().create_resource_change_transaction(
                        self.get_resource_state_uuid(), change.component_name, change
                    )
                except Exception as e:
                    print(e)
                    print(f"Error Creating Transaction: {change}")
                    raise e

                ruuid = (
                    change.new_resource.ruuid
                    if change.new_resource
                    else change.previous_resource.ruuid
                )

                # The Previous output is used by the mappers to make changes to the underlying resources.
                previous_output = (
                    self.get_backend().get_cloud_output_by_name(
                        self.get_resource_state_uuid(),
                        change.component_name,
                        ruuid,
                        change.previous_resource.name,
                    )
                    if not change.action_type == Resource_Change_Type.CREATE
                    else {}
                )

                try:
                    # Substitute the model with a model that has the cloud outputs evaluated.
                    (
                        new_evaluated_resource,
                        evaluated_keys,
                    ) = self.evaluate_and_replace_cloud_output(
                        change.component_name, change.new_resource
                    )
                    previous_evaluated_resource = (
                        self.evaluate_and_replace_previous_cloud_output(
                            change.component_name, change.previous_resource
                        )
                    )

                    # If there was no cloud output in the resource, then the evaluated resources will equal the original resources
                    # so using that value is safe.
                    _evaluated_change = Resource_Difference(
                        change.action_type,
                        change.component_name,
                        previous_evaluated_resource,
                        new_evaluated_resource,
                    )

                except Exception as e:
                    print(e)
                    print(f"Error evaluating cloud output from change: {change}")
                    raise e

                try:
                    # Deploy the changes to the cloud using the defined mapper for the resource.
                    log.debug("evaluated information %s", _evaluated_change)
                    output_task.update(advance=5, comment="Deploying on Cloud :cloud:")
                    mapper = self.get_mapper_namespace().get(ruuid)

                    # If the resource change type is a renaming of the resource, then it should not call to the mapper
                    cloud_output = (
                        mapper.deploy_resource(
                            transaction_token,
                            namespace_token,
                            _evaluated_change,
                            previous_output,
                            output_task,
                        )
                        if _evaluated_change.action_type
                        != Resource_Change_Type.UPDATE_NAME
                        else previous_output
                    )

                except Exception as e:
                    self.get_backend().fail_resource_change(
                        self.get_resource_state_uuid(),
                        change.component_name,
                        change,
                        transaction_token,
                        {"message": "deployment error"},
                    )
                    output_task.update(
                        advance=10,
                        comment="Failed because mapper raised error :cross_mark:",
                    )
                    print(e)
                    raise e

                try:
                    if change.action_type == Resource_Change_Type.CREATE:
                        cloud_output[
                            "cloud_region"
                        ] = Workspace.instance().settings.AWS_REGION

                    output_task.update(
                        advance=3, comment="Completing transaction with Backend"
                    )

                    self.get_backend().complete_resource_change(
                        self.get_resource_state_uuid(),
                        change.component_name,
                        change,
                        transaction_token,
                        cloud_output,
                        evaluated_keys,
                    )

                except Exception as e:
                    self.get_backend().fail_resource_change(
                        self.get_resource_state_uuid(),
                        change.component_name,
                        change,
                        transaction_token,
                        {"message": "backend error"},
                    )
                    output_task.update(
                        advance=10,
                        comment="Failed because backend raised error :cross_mark:",
                    )
                    print(e)
                    raise e

            elif isinstance(change, Resource_Reference_Difference):
                output_task.update(
                    advance=5,
                    comment=f'{"Creating" if change.action_type == Resource_Reference_Change_Type.CREATE else "Removing"} Reference',
                )
                self.get_backend().resolve_reference_change(
                    self.get_resource_state_uuid(), change
                )

            elif isinstance(change, Component_Difference):
                output_task.update(advance=5, comment="Updating Component in Backend")
                self.get_backend().update_component(
                    self.get_resource_state_uuid(), change
                )

            else:
                raise Exception(
                    f"Trying to deploy node {change} but it is not a correct type "
                )

            output_task.update(completed=10, comment="Completed :white_check_mark:")

        return deploy_change

    @wrap_phase([Workspace_State.EXECUTING_BACKEND])
    def evaluate_and_replace_cloud_output(
        self, component_name: str, original_resource: TaggableResourceModel
    ) -> Tuple[TaggableResourceModel, Optional[Dict]]:
        """Replace the Cloud Output object in the given resource

        Args:
            component_name (str)
            original_resource (TaggableResourceModel)

        Returns:
            Tuple[TaggableResourceModel, Dict]
        """
        if not original_resource:
            return original_resource, None

        original_resource_dict = frozendict(original_resource.dict())

        def _resolver(ruuid, name, key) -> Any:
            return self.get_backend().get_cloud_output_value_by_name(
                self.get_resource_state_uuid(), component_name, ruuid, name, key
            )

        updated_resource, resolved_value = self._recursive_replace_output(
            _resolver, original_resource_dict, {}
        )

        evaluated_resource = original_resource.__class__(**updated_resource)

        return evaluated_resource, resolved_value

    @wrap_phase([Workspace_State.EXECUTING_BACKEND])
    def evaluate_and_replace_previous_cloud_output(
        self, component_name: str, previous_resource: TaggableResourceModel
    ) -> TaggableResourceModel:
        """Replace the Cloud Output object in the given resource based on the previous cloud output values

        Args:
            component_name (str)
            previous_resource (TaggableResourceModel)

        Returns:
            Tuple[TaggableResourceModel, Dict]
        """

        if not previous_resource:
            return previous_resource

        original_resource_dict = frozendict(previous_resource.dict())

        def wrap_resolver() -> Callable:
            previous_resolved_values = (
                self.get_backend()
                .get_component(self.get_resource_state_uuid(), component_name)
                .previous_resolved_cloud_values
            )

            if not previous_resolved_values:
                raise Exception

            previous_resource_resolved_values = previous_resolved_values.get(
                f"{previous_resource.ruuid};{previous_resource.name}"
            )

            def _resolver(ruuid, name, key) -> Any:

                if not previous_resource_resolved_values:
                    raise Exception

                key = f"{ruuid};{name};{key}"

                if key not in previous_resource_resolved_values:
                    raise Exception

                return previous_resource_resolved_values.get(key)

            return _resolver

        updated_resource, _ = self._recursive_replace_output(
            wrap_resolver(), original_resource_dict, {}
        )

        evaluated_resource = previous_resource.__class__(**updated_resource)

        return evaluated_resource

    def _recursive_replace_output(
        self, resolver: Callable, original: Any, resolved_values: Dict = {}
    ) -> Tuple[Any, Dict]:
        """Recursively replace any output

        Args:
            resolver (Callable)
            original (Any)
            resolved_values (Dict, optional): Defaults to {}.

        Returns:
            Tuple[Any, Dict]
        """
        # This function works over ImmutableModel that were converted using the `.dict` method. Therefore,
        # the collections will be `frozendict` and `frozenset` instead of `dict` and `list`

        if isinstance(original, frozendict):
            if "id" in original and original.get("id") == "cdev_cloud_output":

                _value = resolver(
                    original.get("ruuid"), original.get("name"), original.get("key")
                )

                values_key = f"{original.get('ruuid')};{original.get('name')};{original.get('key')}"
                resolved_values[values_key] = _value

                if original.get("output_operations"):
                    return (
                        evaluate_dynamic_output(
                            _value, cloud_output_dynamic_model(**original)
                        ),
                        resolved_values,
                    )

                return _value, resolved_values

            rv = {}
            for k, v in original.items():
                new_v, tmp_resolved_values = self._recursive_replace_output(
                    resolver, v, resolved_values
                )

                rv[k] = new_v

                resolved_values.update(tmp_resolved_values)

            return frozendict(rv), resolved_values

        elif isinstance(original, frozenset):
            rv = []
            for x in original:
                new_v, tmp_resolved_values = self._recursive_replace_output(resolver, x)

                rv.append(new_v)

                resolved_values.update(tmp_resolved_values)

            return frozenset(rv), resolved_values

        return original, resolved_values

    @wrap_phase([Workspace_State.INITIALIZED])
    def execute_command(self, command: str, args: List, output: OutputManager) -> None:
        """Find the desired command based on the search path and execute it with the given arguments.

        Args:
            command (str): The full command to search for. can be '.' separated to denote search path.
            args (List): The command lines arguments to pass to the command.
            output (OutputManager): Use to print information
        Raises:
            KeyError: Raises an exception.
        """

        # Command in list form
        command_list = command.split(".")

        # Create list of all directories to start searching in
        all_search_locations_list = self.get_commands()

        obj, program_name, command_name, is_command = find_specified_command(
            command_list, all_search_locations_list, output=output
        )

        if is_command:
            if not isinstance(obj, BaseCommand):
                raise Exception

            args = [program_name, command_name, *args]
            obj.run_from_command_line(args)

        else:
            if not isinstance(obj, BaseCommandContainer):
                raise Exception

            obj.display_help_message()


class WorkspaceManager:
    def create_new_workspace(
        self, workspace_info: Workspace_Info, *posargs, **kwargs
    ) -> None:
        """Create a new workspace based on the information provided.

        Args:
            workspace_info (Workspace_Info): information about the backend configuration

        Raises:
            WorkSpaceAlreadyCreated
        """
        raise NotImplementedError

    def check_if_workspace_exists(self, *posargs, **kwargs) -> bool:
        """Check if a workspace exists

        Raises:
            NotImplementedError

        Returns:
            bool
        """
        raise NotImplementedError

    def load_workspace_configuration(self, *posargs, **kwargs) -> Workspace_Info:
        """Load the configuration of the workspace

        Raises:
            NotImplementedError

        Returns:
            Workspace_Info
        """
        raise NotImplementedError

    def load_workspace(self, *posargs, **kwargs) -> Workspace:
        """Load a workspace

        Raises:
            NotImplementedError

        Returns:
            Workspace
        """
        raise NotImplementedError


def load_workspace(config: Workspace_Info) -> Workspace:
    """Load the workspace from the given configuration

    Args:
        config (Workspace_Info)

    Raises:
        Exception

    Returns:
        Workspace
    """
    try:
        workspace_module = module_loader.import_module(config.python_module)
    except Exception:
        raise WorkspaceInfoError(
            error_message=f"Could not load {config.python_module} as a python module"
        )

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
        raise WorkspaceInfoError(
            error_message=f"Could not find {config.python_class} in {config.python_module} to load as workspace"
        )

    try:
        workspace_obj = workspace_class()

    except Exception:
        raise WorkspaceInfoError(
            error_message=f"Could not load type {workspace_class} as workspace"
        )

    return workspace_obj


def initialize_workspace(workspace: Workspace, workspace_info: Workspace_Info) -> None:
    """Initialize the given workspace

    Args:
        workspace (Workspace): _description_
        workspace_info (Workspace_Info): _description_

    Raises:
        e: _description_
    """
    workspace.set_state(Workspace_State.INITIALIZING)

    # initialize the backend obj with the provided configuration values
    workspace.initialize_workspace(
        settings_info=workspace_info.settings_info,
        backend_info=workspace_info.backend_info,
        resource_state_uuid=workspace_info.resource_state_uuid,
        initialization_modules=workspace_info.initialization_modules,
        configuration=workspace_info.config,
    )

    workspace.set_state(Workspace_State.INITIALIZED)
