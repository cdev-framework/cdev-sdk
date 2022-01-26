from enum import Enum
import importlib
import inspect
import json
import os
import sys
from typing import Callable, List, Dict, Optional, Any, Tuple, Union
from pydantic.main import BaseModel

from pydantic.types import DirectoryPath, FilePath

from ..constructs.backend import Backend, Backend_Configuration, load_backend
from ..constructs.mapper import CloudMapper
from ..constructs.components import Component
from ..constructs.workspace import (
    Workspace_State,
    Workspace_Info,
    Workspace,
    WorkspaceManager,
    wrap_phase,
)

from ..settings import SETTINGS as cdev_settings

from ..utils import module_loader, file_writer


DEFAULT_COMMAND_LOCATIONS = [
    'core.resources.simple'
]


class local_workspace_configuration(BaseModel):
    initialization_module: str
    backend_configuration: Backend_Configuration
    resource_state_uuid: Optional[str]


class local_workspace(Workspace):
    """
    A singleton that encapsulates the configuration of a workspace that is implemented on the local filesystem. The singleton can be accessed during different
    parts of the lifecycle of a cdev core command execution. When this singleton is created, it is registered as the global workspace for that execution.
    """

    _instance = None

    _COMMANDS = DEFAULT_COMMAND_LOCATIONS
    _MAPPERS = []
    _COMPONENTS = []

    _resource_state_uuid: str = None

    _backend: Backend = None

    _state: Workspace_State = Workspace_State.UNINITIALIZED

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Workspace, cls).__new__(cls)
            # Put any initialization here.

            cls._instance.set_state(Workspace_State.UNINITIALIZED)

            # Load the backend
            cls._instance._backend = None

            cls._instance._COMMANDS = DEFAULT_COMMAND_LOCATIONS
            cls._instance._MAPPERS = []
            cls._instance._COMPONENTS = []
            cls._instance._resource_state_uuid = None

            Workspace.set_global_instance(cls._instance)

        return cls._instance

    @classmethod
    def terminate_singleton(cls):
        cls._instance = None

    def initialize_workspace(
        self, workspace_configuration_dict: local_workspace_configuration
    ):

        # It is the responsibility of the higher up callers to set the correct states for initialization.
        # This allows the flexibility of higher up frameworks injecting initialization steps into the process.
        workspace_configuration = local_workspace_configuration(
            **workspace_configuration_dict
        )
        
        try:
            backend_config = workspace_configuration.backend_configuration
            self.set_backend(load_backend(backend_config))
        except Exception as e:
            print(f"Could not load the load backend")
            raise e

        module_loader.import_module(workspace_configuration.initialization_module, denote_output=True)
        
        if workspace_configuration.resource_state_uuid:
            if not workspace_configuration.resource_state_uuid in set(
                [x.uuid for x in self._backend.get_top_level_resource_states()]
            ):
                raise Exception(
                    f"{workspace_configuration.resource_state_uuid} not in loaded backend ({self._backend.get_top_level_resource_states()})"
                )

        self.set_resource_state_uuid(workspace_configuration.resource_state_uuid)
        
        

    def destroy_workspace(self):
        Workspace.destroy_workspace(self)
        local_workspace.terminate_singleton()

    ################
    ##### State
    ################
    def set_state(self, value: Workspace_State):
        self._state = value

    def get_state(self) -> Workspace_State:
        return self._state

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

        self._MAPPERS.append(mapper)

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_BACKEND])
    def get_mappers(self) -> List[CloudMapper]:
        return self._MAPPERS

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_BACKEND])
    def get_mapper_namespace(self) -> Dict:
        rv = {}
        mappers: List[CloudMapper] = self.get_mappers()

        for mapper in mappers:
            for namespace in mapper.get_namespaces():
                rv[namespace] = mapper

        return rv

    #################
    ##### Commands
    #################
    @wrap_phase([Workspace_State.INITIALIZING])
    def add_command(self, command_location: str):
        self._COMMANDS.append(command_location)

    @wrap_phase([Workspace_State.INITIALIZING])
    def add_commands(self, command_locations: List[str]):
        for command_location in command_locations:
            self.add_command(command_location)

    @wrap_phase([Workspace_State.INITIALIZED])
    def get_commands(self) -> List[str]:
        return self._COMMANDS

    #################
    ##### Components
    #################
    @wrap_phase([Workspace_State.INITIALIZING])
    def add_component(self, component: Component):
        self._COMPONENTS.append(component)

    @wrap_phase([Workspace_State.INITIALIZING])
    def add_components(self, components: List[Component]):
        for component in components:
            self.add_component(component)

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_FRONTEND])
    def get_components(self) -> List[Component]:
        return self._COMPONENTS

    #################
    ##### Backend
    #################
    @wrap_phase([Workspace_State.INITIALIZING])
    def set_backend(self, backend: Backend):
        if not isinstance(backend, Backend):
            raise Exception("Not a backend object")

        self._backend = backend

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_FRONTEND, Workspace_State.EXECUTING_BACKEND])
    def get_backend(self) -> Backend:
        return self._backend

    @wrap_phase([Workspace_State.INITIALIZING])
    def set_resource_state_uuid(self, resource_state_uuid: str):
        self._resource_state_uuid = resource_state_uuid

    @wrap_phase([Workspace_State.INITIALIZED, Workspace_State.EXECUTING_FRONTEND,  Workspace_State.EXECUTING_BACKEND])
    def get_resource_state_uuid(self) -> str:
        return self._resource_state_uuid


class local_workspace_manager(WorkspaceManager):
    def __init__(
        self,
        base_dir: DirectoryPath,
        workspace_dir: str = None,
        workspace_filename: str = None,
    ) -> None:
        self.base_dir = base_dir
        self.workspace_dir = (
            workspace_dir if workspace_dir else cdev_settings.get("ROOT_FOLDER_NAME")
        )
        self.workspace_filename = (
            workspace_filename
            if workspace_filename
            else cdev_settings.get("WORKSPACE_FILE_NAME")
        )

    def create_new_workspace(self, workspace_info: Workspace_Info):
        """
        Create a new workspace based on the information provided.

        Args:
            workspace_info (Workspace_Info): information about the backend configuration

        Raises:
            WorkSpaceAlreadyCreated
        """
        base_cdev_dir = os.path.join(self.base_dir, self.workspace_dir)
        if not os.path.isdir(base_cdev_dir):
            os.mkdir(base_cdev_dir)

        file_writer.safe_json_write(
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
