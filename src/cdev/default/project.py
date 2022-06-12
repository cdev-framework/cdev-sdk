import json
from pydantic.types import FilePath
import os
from typing import Dict, List, Any, Tuple


from cdev.constructs.project import Project, Project_State, Project_Info, wrap_phases
from cdev.default.environment import local_environment

from core.constructs.backend import load_backend, Backend_Configuration
from core.constructs.mapper import CloudMapper
from core.constructs.components import Component
from core.constructs.workspace import Workspace_State, Workspace_Info
from core.constructs.settings import Settings_Info, Settings
from core.constructs.cloud_output import Cloud_Output

from core.utils import file_manager, paths as paths_utils

from ..constructs.environment import environment_info, Environment


class local_project_info(Project_Info):
    settings_directory: str
    initialization_module: str

    def __init__(__pydantic_self__, **data: Any) -> None:
        """"""
        super().__init__(**data)


class local_project(Project):
    """
    An implementation of the Project API that works for simple local development.

    Arguments:
        project_info (local_project_info): Info of the project
        project_info_file (FilePath): Path to save configuration file

    """

    _instance = None

    _project_info_location: FilePath = None
    _project_info: local_project_info = None
    _current_state: Project_State = None

    def __new__(cls, project_info: local_project_info, project_info_filepath: FilePath):
        if cls._instance is None:
            cls._instance = super(Project, cls).__new__(cls)

            cls._instance._project_info_location = project_info_filepath
            cls._instance._project_info = project_info

            cls._instance.set_state(Project_State.INFO_LOADED)

            Project.set_global_instance(cls._instance)

        return cls._instance

    @classmethod
    def terminate_singleton(cls) -> None:
        cls._instance = None

    def initialize_project(self) -> None:
        current_env = self.get_current_environment()
        self.set_state(Project_State.INITIALIZING)

        if current_env:
            current_env.initialize_environment()
        self.set_state(Project_State.INITIALIZED)

    def terminate_project(self) -> None:
        Project.remove_global_instance(self)

    def set_name(self, name: str) -> None:
        """
        Set the name of this Project

        Args:
            name (str): name of the Project
        """
        self._project_name = name

    def get_name(self) -> str:
        """
        Get the name of this Project

        Returns:
            name (str)
        """
        return self._project_name

    def get_state(self) -> Project_State:
        return self._current_state

    def set_state(self, new_state: Project_State) -> None:
        self._current_state = new_state

    # Note that the class methods should not include doc strings so that they inherit the doc string of the
    # parent class.

    @wrap_phases([Project_State.INFO_LOADED])
    def create_environment(
        self, environment_name: str, backend_configuration: Backend_Configuration = None
    ) -> None:
        self._load_info()

        if not backend_configuration:
            backend_configuration = self._create_default_backend_configuration()

        try:
            resource_state_id = load_backend(
                backend_configuration
            ).create_resource_state(environment_name)
        except Exception as e:
            raise e

        base_directory = os.path.dirname(self._project_info.settings_directory)

        _base_settings_file = os.path.join(
            self._project_info.settings_directory, f"base_settings.py"
        )
        _environment_settings_file = os.path.join(
            self._project_info.settings_directory, f"{environment_name}_settings.py"
        )

        settings_files = [_base_settings_file, _environment_settings_file]

        [paths_utils.touch_file(x) for x in settings_files]

        user_setting_modules = [
            # set the settings modules as python modules
            os.path.relpath(x, start=base_directory,)[
                :-3
            ].replace("/", ".")
            for x in settings_files
        ]

        _abs_secrets_dir = os.path.join(
            self._project_info.settings_directory, f"{environment_name}_secrets"
        )
        paths_utils.mkdir(_abs_secrets_dir)
        relative_secret_dir = os.path.relpath(_abs_secrets_dir, start=base_directory)

        settings = Settings_Info(
            base_class="core.constructs.settings.Settings",
            user_setting_module=user_setting_modules,
            secret_dir=relative_secret_dir,
        )

        self._project_info.environments.append(
            environment_info(
                name=environment_name,
                workspace_info=Workspace_Info(
                    python_module="core.default.workspace",
                    python_class="local_workspace",
                    settings_info=settings,
                    backend_info=backend_configuration,
                    resource_state_uuid=resource_state_id,
                    initialization_modules=[self._project_info.initialization_module],
                ),
            )
        )

        self._write_info()

    @wrap_phases([Project_State.INFO_LOADED])
    def destroy_environment(self, environment_name: str) -> None:
        self._load_info()

        self._project_info.environments = [
            x for x in self._project_info.environments if x.name != environment_name
        ]

        self._write_info()

    @wrap_phases([Project_State.INFO_LOADED])
    def get_all_environment_names(self) -> List[str]:
        self._load_info()

        return [x.name for x in self._project_info.environments]

    @wrap_phases([Project_State.INFO_LOADED])
    def set_current_environment(self, environment_name: str) -> None:
        self._load_info()

        if environment_name not in self.get_all_environment_names():
            raise Exception

        self._project_info.current_environment_name = environment_name

        self._write_info()

    @wrap_phases([Project_State.INFO_LOADED])
    def get_environment_settings_info(
        self, environment_name: str = None
    ) -> Settings_Info:
        if not environment_name:
            environment_name = self.get_current_environment_name()

        self._load_info()

        environment_info = self._get_environment_info(environment_name)

        return environment_info.workspace_info.settings_info

    @wrap_phases([Project_State.INFO_LOADED])
    def update_environment_settings_info(
        self, new_value: Settings_Info, environment_name: str = None
    ) -> None:
        if not environment_name:
            environment_name = self.get_current_environment_name()

        self._load_info()

        # Remove the old environment
        previous_environment_var = self._get_environment_info(environment_name)
        previous_environment_var.workspace_info.settings_info = new_value

        self._project_info.environments = [
            x for x in self._project_info.environments if not x.name == environment_name
        ]

        self._project_info.environments.append(previous_environment_var)

        self._write_info()

    def get_environment(self, environment_name: str) -> Environment:
        self._load_info()

        environment_info = self._get_environment_info(environment_name)

        return local_environment(environment_info)

    def get_current_environment_name(self) -> str:
        self._load_info()

        return self._project_info.current_environment_name

    def get_current_environment(self) -> Environment:
        self._load_info()

        if not self._project_info.current_environment_name:
            return None

        return self.get_environment(self._project_info.current_environment_name)

    def _get_environment_info(self, name: str) -> environment_info:
        self._load_info()

        lookup_dict = {x.name: x for x in self._project_info.environments}

        if not name in lookup_dict:
            raise Exception(f"No environment with name {name}")

        return lookup_dict.get(name)

    ############################
    ##### Runtime Settings
    ############################
    @property
    def settings(self) -> Settings:
        return self.get_current_environment().get_workspace().settings

    @settings.setter
    def settings(self, value: Settings) -> None:
        self.get_current_environment().get_workspace().settings = value

    #######################
    ##### Display Output
    #######################
    def display_output(self, tag: str, output: Cloud_Output) -> None:
        """Display the output from a Resource or Reference after a process has completed

        Args:
            tag: A key value to display with the output
            output: The Cloud Output to render
        """
        self.get_current_environment().get_workspace().display_output(tag, output)

    def render_outputs(self) -> List[Tuple[str, Any]]:
        """Render the output associated with the Workspace

        Returns:
            List[Tuple[str, Any]]: The List of outputs with their associated tag

        """
        return self.get_current_environment().get_workspace().render_outputs()

    #################
    ##### Mappers
    #################
    @wrap_phases([Project_State.INITIALIZING])
    def add_mapper(self, mapper: CloudMapper) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_mapper(mapper)

    @wrap_phases([Project_State.INITIALIZING])
    def add_mappers(self, mappers: List[CloudMapper]) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_mappers(mappers)

    @wrap_phases([Project_State.INITIALIZED])
    def get_mappers(self) -> List[CloudMapper]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_mappers()

    @wrap_phases([Project_State.INITIALIZED])
    def get_mapper_namespace(self) -> Dict:
        ws = self.get_current_environment().get_workspace()
        return ws.get_mapper_namespace()

    #################
    ##### Commands
    #################
    @wrap_phases([Project_State.INITIALIZING])
    def add_command(self, command_location: str) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_command(command_location)

    @wrap_phases([Project_State.INITIALIZING])
    def add_commands(self, command_locations: List[str]) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_commands(command_locations)

    @wrap_phases([Project_State.INITIALIZED])
    def get_commands(self) -> List[str]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_commands()

    #################
    ##### Components
    #################
    @wrap_phases([Project_State.INITIALIZING])
    def add_component(self, component: Component) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_component(component)

    @wrap_phases([Project_State.INITIALIZING])
    def add_components(self, components: List[Component]) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_components(components)

    @wrap_phases([Project_State.INITIALIZED])
    def get_components(self) -> List[Component]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_components()

    ##########################
    ##### Internal Helpers
    ##########################
    def _write_info(self) -> None:
        file_manager.safe_json_write(
            self._project_info.dict(), self._project_info_location
        )

    def _load_info(self):
        with open(self._project_info_location, "r") as fh:
            self._project_info = local_project_info(**json.load(fh))

    def _create_default_backend_configuration(self) -> Backend_Configuration:
        self._load_info()

        return self._project_info.default_backend_configuration

    def _get_environment_info(self, environment_name: str) -> environment_info:
        rv = next(
            [x for x in self._project_info.environments if x.name == environment_name],
            None,
        )

        if not rv:
            raise Exception

        return rv
