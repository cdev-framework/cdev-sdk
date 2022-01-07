import json
from pydantic.types import FilePath
from typing import Dict, List, Callable, Any, TypeVar


from cdev.constructs.project import Project, Project_State, project_info, wrap_phase
from cdev.default.environment import local_environment
from core.constructs.backend import Backend, load_backend

from core.constructs.mapper import CloudMapper
from core.constructs.components import Component
from core.constructs.workspace import Workspace_State


from core.constructs.workspace import Workspace_Info
from core.utils import file_writer

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
    
    def __new__(cls, project_info_location: FilePath):
        if cls._instance is None:
            cls._instance = super(Project, cls).__new__(cls)
            # Put any initialization here.
            cls._instance._project_info_location = project_info_location

            cls._instance._load_state()

            cls._instance._backend = load_backend(cls._instance._central_state.backend_info)

            # Load the backend 
            cls._instance._current_environment = None

            Project.set_global_instance(cls._instance)

        return cls._instance


    @classmethod
    def terminate_singleton(cls):
        cls._instance = None

    def initialize_project(self):
        current_env = self.get_current_environment()
        current_env.initialize_environment()


    def terminate_project(self):
        Project.remove_global_instance(self)


    def get_state(self) -> Project_State:
        environment = self.get_current_environment()
        return WORKSPACE_STATE_TO_PROJECT_STATE.get(environment.get_workspace().get_state())


    @wrap_phase(Project_State.INITIALIZED)
    def create_environment(self, environment_name: str):
        self._load_state()
        resource_state_id = self._backend.create_resource_state(environment_name)

        workspace_config = {
            'backend_configuration': self._central_state.backend_info
        }

        workspace_config['resource_state_uuid'] = resource_state_id
        workspace_config['initialization_module'] = 'cdev_project'

        self._central_state.environments.append( 
            environment_info(
                environment_name,
                Workspace_Info(
                    "core.default.workspace",
                    "local_workspace",
                    workspace_config
                )
            )
        )

        self._write_state()


    @wrap_phase(Project_State.INITIALIZED)
    def destroy_environment(self, environment_name: str) -> None:
        self._load_state()

        self._central_state.environments = [x for x in self._central_state.environments if x.name != environment_name]

        self._write_state()


    @wrap_phase(Project_State.UNINITIALIZED)
    def get_all_environment_names(self) -> List[str]:
        """
        Get the list of all the environments for this project
        """
        self._load_state()


        return [x.name for x in self._central_state.environments]

    @wrap_phase(Project_State.UNINITIALIZED)
    def set_current_environment(self, environment_name: str):
        self._load_state()

        self._central_state.current_environment = environment_name

        self._write_state()


    def get_environment(self, environment_name: str) -> Environment:
        self._load_state()

        environment_info =  next(x for x in self._central_state.environments if x.name == environment_name)

        return local_environment(environment_info)


    def get_current_environment_name(self) -> str:
        self._load_state()

        return self._central_state.current_environment


    def get_current_environment(self) -> Environment:
        self._load_state()

        return self.get_environment(self._central_state.current_environment)


    def _get_environment_info(self, name: str) -> environment_info:
        self._load_state()
        
        lookup_dict = {x.name:x for x in self._central_state.environments}

        if not name in lookup_dict:
            raise Exception(f"No environment with name {name}")


        return lookup_dict.get(name)


    
    #################
    ##### Mappers
    #################
    @wrap_phase(Workspace_State.INITIALIZING)
    def add_mapper(self, mapper: CloudMapper ) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_mapper(mapper)


    @wrap_phase(Workspace_State.INITIALIZING)
    def add_mappers(self, mappers: List[CloudMapper] ) -> None:
       ws = self.get_current_environment().get_workspace()
       ws.add_mappers(mappers)


    @wrap_phase(Workspace_State.INITIALIZED)
    def get_mappers(self) -> List[CloudMapper]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_mappers()


    @wrap_phase(Workspace_State.INITIALIZED)
    def get_mapper_namespace(self) -> Dict:
        ws = self.get_current_environment().get_workspace()
        return ws.get_mapper_namespace()



    #################
    ##### Commands
    #################
    @wrap_phase(Workspace_State.INITIALIZING)
    def add_command(self, command_location: str):
        ws = self.get_current_environment().get_workspace()
        ws.add_command(command_location)


    @wrap_phase(Workspace_State.INITIALIZING)
    def add_commands(self, command_locations: List[str]):
        ws = self.get_current_environment().get_workspace()
        ws.add_commands(command_locations)
    

    @wrap_phase(Workspace_State.INITIALIZED)
    def get_commands(self) -> List[str]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_commands()


    
    #################
    ##### Components
    #################
    @wrap_phase(Workspace_State.INITIALIZING)
    def add_component(self, component: Component):
        ws = self.get_current_environment().get_workspace()
        ws.add_component(component)


    @wrap_phase(Workspace_State.INITIALIZING)
    def add_components(self, components: List[Component]):
        ws = self.get_current_environment().get_workspace()
        ws.add_components(components)


    @wrap_phase(Workspace_State.INITIALIZED)
    def get_components(self) -> List[Component]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_components()


    def _write_state(self):
        file_writer.safe_json_write(self._central_state.dict(), self._project_info_location)


    def _load_state(self) -> project_info:
        with open(self._project_info_location, 'r') as fh:
            self._central_state = project_info(**json.load(fh))
