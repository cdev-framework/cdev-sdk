import json
from pydantic.types import FilePath
from typing import Dict, List, Callable, Any, TypeVar, Tuple


from cdev.constructs.project import Project, Project_State, project_info, wrap_phases
from cdev.default.environment import local_environment
from core.constructs.backend import Backend, load_backend

from core.constructs.mapper import CloudMapper
from core.constructs.components import Component
from core.constructs.workspace import Workspace_State

from core.constructs.workspace import Workspace_Info
from core.constructs.settings import Settings_Info, Settings
from core.constructs.cloud_output import Cloud_Output

from core.utils import file_manager

from ..constructs.environment import environment_info, Environment

WORKSPACE_STATE_TO_PROJECT_STATE = {
    Workspace_State.UNINITIALIZED: Project_State.UNINITIALIZED,
    Workspace_State.INITIALIZING: Project_State.INITIALIZING,
    Workspace_State.INITIALIZED: Project_State.INITIALIZED,
}


class local_project(Project):
    """
    An implementation of the Project API that works for simple local development.

    Arguments:
        project_info_location (FilePath): Path the configuration json file

    """

    _instance = None

    _current_environment: Environment = None
    _project_info_location: FilePath = None

    _central_state: project_info
    _backend: Backend = None
    _project_state: Project_State = None
    _project_name: str = None

    def __new__(cls, project_info_location: FilePath):
        if cls._instance is None:
            cls._instance = super(Project, cls).__new__(cls)
            # Put any initialization here.
            cls._instance._project_info_location = project_info_location

            cls._instance._load_state()

            cls._instance.set_name(cls._instance._central_state.project_name)

            cls._instance._backend = load_backend(
                cls._instance._central_state.backend_info
            )

            # Load the backend
            cls._instance._current_environment = None
            
            cls._instance.set_state(Project_State.UNINITIALIZED)

            Project.set_global_instance(cls._instance)


        return cls._instance

    @classmethod
    def terminate_singleton(cls):
        cls._instance = None

    def initialize_project(self):
        self.set_state(Project_State.INITIALIZING)
        current_env = self.get_current_environment()
        
        if current_env:
            current_env.initialize_environment()
        self.set_state(Project_State.INITIALIZED)

    def terminate_project(self):
        Project.remove_global_instance(self)


    def set_name(self, name: str):
        """
        Set the name of this Project

        Args:
            name (str): name of the Project
        """
        self._project_name = name


    def get_name(self):
        """
        Get the name of this Project

        Returns:
            name (str)
        """
        return self._project_name

    def get_state(self) -> Project_State:
        return self._project_state

    def set_state(self, new_state: Project_State):
        self._project_state = new_state

    # Note that the class methods should not include doc strings so that they inherit the doc string of the 
    # parent class. 

    @wrap_phases([Project_State.INITIALIZED, Project_State.UNINITIALIZED])
    def create_environment(self, environment_name: str, settings_files: Dict[str,str] = None):
        self._load_state()
        resource_state_id = self._backend.create_resource_state(environment_name)

        workspace_config = {"backend_configuration": self._central_state.backend_info}

        workspace_config["resource_state_uuid"] = resource_state_id
        workspace_config["initialization_module"] = "src.cdev_project"

            
        settings = Settings_Info(
            base_class = "core.constructs.settings.Settings"
        ) if not settings_files else Settings_Info(
            base_class = "core.constructs.settings.Settings",
            user_setting_module=settings_files.get('user_setting_module'),
            secret_dir=settings_files.get('secret_dir'),
        )

        self._central_state.environments.append(
            environment_info(
                environment_name,
                Workspace_Info(
                    "core.default.workspace", 
                    "local_workspace", 
                    settings,
                    workspace_config
                ),
            )
        )

        self._write_state()

    @wrap_phases([Project_State.INITIALIZED, Project_State.UNINITIALIZED])
    def destroy_environment(self, environment_name: str) -> None:
        self._load_state()

        self._central_state.environments = [
            x for x in self._central_state.environments if x.name != environment_name
        ]

        self._write_state()

    @wrap_phases([Project_State.INITIALIZED, Project_State.UNINITIALIZED])
    def get_all_environment_names(self) -> List[str]:
        self._load_state()

        return [x.name for x in self._central_state.environments]

    @wrap_phases([Project_State.INITIALIZED, Project_State.UNINITIALIZED])
    def set_current_environment(self, environment_name: str):
        self._load_state()

        if not environment_name in self.get_all_environment_names():
            raise Exception

        self._central_state.current_environment = environment_name

        self._write_state()

    def get_environment(self, environment_name: str) -> Environment:
        self._load_state()

        environment_info = next(
            x for x in self._central_state.environments if x.name == environment_name
        )

        return local_environment(environment_info)

    def get_current_environment_name(self) -> str:
        self._load_state()

        return self._central_state.current_environment

    def get_current_environment(self) -> Environment:
        self._load_state()

        if not self._central_state.current_environment:
            return None

        return self.get_environment(self._central_state.current_environment)

    def _get_environment_info(self, name: str) -> environment_info:
        self._load_state()

        lookup_dict = {x.name: x for x in self._central_state.environments}

        if not name in lookup_dict:
            raise Exception(f"No environment with name {name}")

        return lookup_dict.get(name)

    ############################
    ##### Settings
    ############################
    @property
    def settings(self) -> Settings:
        return self.get_current_environment().get_workspace().settings

    
    @settings.setter
    def settings(self, value: Settings):
        self.get_current_environment().get_workspace().settings= value


    def get_settings_info(self, environment_name: str =  None) -> Settings_Info:
        if not environment_name:
            environment_name = self.get_current_environment_name()


        self._load_state()
        
        if not environment_name in [x.name for x in self._central_state.environments]:
            raise Exception(f"No environment named {environment_name}")


        return [x for x in self._central_state.environments if x.name == environment_name][0].workspace_info.settings_info
    
    def update_settings_info(self, new_value: Settings_Info, environment_name: str = None):
        if not environment_name:
            environment_name = self.get_current_environment_name()
            
        self._load_state()

        # Remove the old environment
        previous_environment_var = [x for x in self._central_state.environments if x.name == environment_name][0]
        previous_environment_var.workspace_info.settings_info = new_value


        self._central_state.environments = [x for x in self._central_state.environments if not x.name == environment_name]

        self._central_state.environments.append(previous_environment_var)

        self._write_state()

    #######################
    ##### Display Output
    #######################
    def display_output(self, tag: str, output: Cloud_Output):
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
    @wrap_phases([Workspace_State.INITIALIZING])
    def add_mapper(self, mapper: CloudMapper) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_mapper(mapper)

    @wrap_phases([Workspace_State.INITIALIZING])
    def add_mappers(self, mappers: List[CloudMapper]) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_mappers(mappers)

    @wrap_phases([Workspace_State.INITIALIZED])
    def get_mappers(self) -> List[CloudMapper]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_mappers()

    @wrap_phases([Workspace_State.INITIALIZED])
    def get_mapper_namespace(self) -> Dict:
        ws = self.get_current_environment().get_workspace()
        return ws.get_mapper_namespace()

    #################
    ##### Commands
    #################
    @wrap_phases([Workspace_State.INITIALIZING])
    def add_command(self, command_location: str):
        ws = self.get_current_environment().get_workspace()
        ws.add_command(command_location)

    @wrap_phases([Workspace_State.INITIALIZING])
    def add_commands(self, command_locations: List[str]):
        ws = self.get_current_environment().get_workspace()
        ws.add_commands(command_locations)

    @wrap_phases([Workspace_State.INITIALIZED])
    def get_commands(self) -> List[str]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_commands()

    #################
    ##### Components
    #################
    @wrap_phases([Workspace_State.INITIALIZING])
    def add_component(self, component: Component):
        ws = self.get_current_environment().get_workspace()
        ws.add_component(component)

    @wrap_phases([Workspace_State.INITIALIZING])
    def add_components(self, components: List[Component]):
        ws = self.get_current_environment().get_workspace()
        ws.add_components(components)

    @wrap_phases([Workspace_State.INITIALIZED])
    def get_components(self) -> List[Component]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_components()

    def _write_state(self):
        file_manager.safe_json_write(
            self._central_state.dict(), self._project_info_location
        )

    def _load_state(self) -> project_info:
        with open(self._project_info_location, "r") as fh:
            self._central_state = project_info(**json.load(fh))
