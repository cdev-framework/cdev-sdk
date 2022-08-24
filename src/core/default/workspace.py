import json
import os
from typing import List, Dict, Optional, Any, Tuple

from pydantic.types import DirectoryPath

from core.constructs.backend import Backend, Backend_Configuration
from core.constructs.mapper import CloudMapper
from core.constructs.components import Component, ComponentModel
from core.constructs.workspace import (
    Workspace_State,
    Workspace_Info,
    Workspace,
    WorkspaceManager,
    wrap_phase,
)
from core.constructs.cloud_output import (
    Cloud_Output,
    cloud_output_dynamic_model,
    evaluate_dynamic_output,
    cloud_output_model,
)
from core.constructs.settings import Settings_Info

from ..utils import file_manager


DEFAULT_COMMAND_LOCATIONS = ["core.default.commands"]

ROOT_FOLDER_NAME = ".cdev"
WORKSPACE_FILE_NAME = "workspace_info.json"


class local_workspace(Workspace):
    """
    A singleton that implements a workspace that is on the local filesystem. The singleton can be accessed during different
    parts of the lifecycle of a cdev core command execution. When this singleton is created, it is registered as the global
    workspace for that execution.
    """

    _instance = None

    _COMMANDS = DEFAULT_COMMAND_LOCATIONS
    _MAPPERS = []
    _COMPONENTS = []
    _OUTPUT: List[Tuple[str, str, cloud_output_model]] = []

    _resource_state_uuid: str = None
    _backend: Backend = None

    _state: Workspace_State = Workspace_State.UNINITIALIZED

    _current_component: str = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Workspace, cls).__new__(cls)
            # Put any initialization here.

            cls._instance.set_state(Workspace_State.UNINITIALIZED)

            # Load the backend
            cls._instance._backend = None
            cls._instance._resource_state_uuid = None

            cls._instance._COMMANDS = DEFAULT_COMMAND_LOCATIONS
            cls._instance._MAPPERS = []
            cls._instance._COMPONENTS = []
            cls._instance._OUTPUT = []

            Workspace.set_global_instance(cls._instance)

        return cls._instance

    @classmethod
    def terminate_singleton(cls) -> None:
        cls._instance = None

    def initialize_workspace(
        self,
        settings_info: Settings_Info,
        backend_info: Backend_Configuration,
        resource_state_uuid: str,
        initialization_modules: Optional[List[str]] = [],
        configuration: Dict = {},
    ) -> None:
        super().initialize_workspace(
            settings_info=settings_info,
            backend_info=backend_info,
            resource_state_uuid=resource_state_uuid,
            initialization_modules=initialization_modules,
            configuration=configuration,
        )

    def destroy_workspace(self) -> None:
        Workspace.destroy_workspace(self)
        local_workspace.terminate_singleton()

    ################
    ##### State
    ################
    def set_state(self, value: Workspace_State) -> None:
        self._state = value

    def get_state(self) -> Workspace_State:
        return self._state

    @wrap_phase([Workspace_State.EXECUTING_FRONTEND])
    def generate_current_state(self) -> List[ComponentModel]:
        rv = []
        for component in self.get_components():
            self._current_component = component.name
            rv.append(component.render())

        return rv

    @wrap_phase([Workspace_State.INITIALIZING])
    def set_resource_state_uuid(self, resource_state_uuid: str) -> None:
        """Set the Resource State UUID to denote the Resource State that this Workspace will execute over.

        Note that this function should only be called during the `Workspace Initialization` part of the Cdev lifecycle.

        Arguments:
            resource_state_uuid (str): Resource State UUID from the Backend
        """
        self._resource_state_uuid = resource_state_uuid

    @wrap_phase(
        [
            Workspace_State.INITIALIZED,
            Workspace_State.EXECUTING_FRONTEND,
            Workspace_State.EXECUTING_BACKEND,
        ]
    )
    def get_resource_state_uuid(self) -> str:
        """Get the Resource State UUID that this Workspace is executing over.

        Note that this function should only be called during the `Workspace Initialized` part of the Cdev lifecycle.

        Returns:
            resource_state_uuid (str): Resource State UUID from the Backend
        """
        return self._resource_state_uuid

    #######################
    ##### Display Output
    #######################
    @wrap_phase(
        [
            Workspace_State.INITIALIZED,
            Workspace_State.EXECUTING_FRONTEND,
            Workspace_State.EXECUTING_BACKEND,
        ]
    )
    def display_output(self, tag: str, output: Cloud_Output) -> None:
        self._OUTPUT.append((tag, self._current_component, output.render()))

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_BACKEND])
    def render_outputs(self) -> List[Tuple[str, Any]]:

        if not self._current_component:
            raise Exception

        rv = []
        backend = self.get_backend()
        for tag, component, cloud_output in self._OUTPUT:
            resolved_value = backend.get_cloud_output_value_by_name(
                self.get_resource_state_uuid(),
                component,
                cloud_output.ruuid,
                cloud_output.name,
                cloud_output.key,
            )

            if isinstance(cloud_output, cloud_output_dynamic_model):
                # If the cloud output object contains computations than evaluate the computations over the cloud output
                resolved_value = evaluate_dynamic_output(resolved_value, cloud_output)

            rv.append((tag, resolved_value))

        return rv

    def clear_output(self) -> None:
        self._OUTPUT = []

    #################
    ##### Mappers
    #################
    @wrap_phase([Workspace_State.INITIALIZING])
    def add_mapper(self, mapper: CloudMapper) -> None:
        if not isinstance(mapper, CloudMapper):
            # TODO Throw error
            print(f"BAD CLOUD MAPPER {mapper}")
            return

        self._MAPPERS.append(mapper)

    @wrap_phase([Workspace_State.INITIALIZING])
    def add_mappers(self, mappers: List[CloudMapper]) -> None:

        for mapper in mappers:
            self.add_mapper(mapper)

        #ANIBAL This mapper may not exist here!
        self._MAPPERS.append(mapper)

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_BACKEND])
    def get_mappers(self) -> List[CloudMapper]:
        return self._MAPPERS

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_BACKEND])
    def get_mapper_namespace(self) -> Dict:
        mappers: List[CloudMapper] = self.get_mappers()

        rv = {}
        for mapper in mappers:
            for namespace in mapper.get_namespaces():
                rv[namespace] = mapper

        return rv

    #################
    ##### Commands
    #################
    @wrap_phase([Workspace_State.INITIALIZING])
    def add_command(self, command_location: str) -> None:
        self._COMMANDS.append(command_location)

    @wrap_phase([Workspace_State.INITIALIZING])
    def add_commands(self, command_locations: List[str]) -> None:
        for command_location in command_locations:
            self.add_command(command_location)

    @wrap_phase([Workspace_State.INITIALIZED])
    def get_commands(self) -> List[str]:
        return self._COMMANDS

    #################
    ##### Components
    #################
    @wrap_phase([Workspace_State.INITIALIZING])
    def add_component(self, component: Component) -> None:
        self._COMPONENTS.append(component)

    @wrap_phase([Workspace_State.INITIALIZING])
    def add_components(self, components: List[Component]) -> None:
        for component in components:
            self.add_component(component)

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_FRONTEND])
    def get_components(self) -> List[Component]:
        return self._COMPONENTS

    #################
    ##### Backend
    #################
    @wrap_phase([Workspace_State.INITIALIZING])
    def set_backend(self, backend: Backend) -> None:
        if not isinstance(backend, Backend):
            raise Exception("Not a backend object")

        self._backend = backend

    @wrap_phase(
        [
            Workspace_State.INITIALIZED,
            Workspace_State.EXECUTING_FRONTEND,
            Workspace_State.EXECUTING_BACKEND,
        ]
    )
    def get_backend(self) -> Backend:
        return self._backend


class local_workspace_manager(WorkspaceManager):
    def __init__(
        self,
        base_dir: DirectoryPath,
        workspace_dir: str = None,
        workspace_filename: str = None,
    ) -> None:
        self.base_dir = base_dir
        self.workspace_dir = workspace_dir if workspace_dir else ROOT_FOLDER_NAME
        self.workspace_filename = (
            workspace_filename if workspace_filename else WORKSPACE_FILE_NAME
        )

    def create_new_workspace(self, workspace_info: Workspace_Info) -> None:
        base_cdev_dir = os.path.join(self.base_dir, self.workspace_dir)
        if not os.path.isdir(base_cdev_dir):
            os.mkdir(base_cdev_dir)

        file_manager.safe_json_write(
            workspace_info.dict(), os.path.join(base_cdev_dir, self.workspace_filename)
        )

    def check_if_workspace_exists(self) -> bool:
        return os.path.isfile(
            os.path.join(self.base_dir, self.workspace_dir, self.workspace_filename)
        )

    def load_workspace_configuration(self) -> Workspace_Info:
        file_location = os.path.join(
            self.base_dir, self.workspace_dir, self.workspace_filename
        )

        with open(file_location, "r") as fh:
            raw_data = json.load(fh)

        try:
            rv = Workspace_Info(**raw_data)

            return rv
        except Exception as e:
            print(e)
            raise e
