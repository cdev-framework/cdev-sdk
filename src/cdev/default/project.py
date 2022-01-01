import json
from typing import Dict, List, Callable
from cdev.constructs.project import Project, project_info

from core.constructs.mapper import CloudMapper
from core.constructs.components import Component
from core.constructs.workspace import Workspace_State
from pydantic.types import FilePath

from ..constructs.environment import environment_info, Environment



def wrap_phase(phase: Workspace_State):
    """
    Annotation that denotes when a function can be executed within the life cycle of a workspace. Throws excpetion if the workspace is not in the correct
    phase. 
    """
    def inner_wrap(func: Callable):
        def wrapper_func(project: 'Project', *func_posargs , **func_kwargs):
            

            environment = project.get_current_environment()
            current_state = environment.get_workspace().get_state()
            if not current_state == phase:
                raise Exception(f"Trying to call {func} while in workspace state {current_state} but need to be in {phase}")

            else:
                
                return func(project, *func_posargs, **func_kwargs) 

        return wrapper_func
    
    return inner_wrap


class local_project(Project):
    """
    A singleton that encapsulates the configuration and high level information needed to construct a project. This singleton
    can be used within the different components to gain information about the higher level project that it is within. 
    """

    _current_environment: Environment = None
    _state_file_location: FilePath = None

    _central_state: project_info
    
    
    def __new__(cls, state_file_location: FilePath):
        if cls._instance is None:
            cls._instance = super(Project, cls).__new__(cls)
            # Put any initialization here.
            cls._instance._state_file_location = state_file_location


            # Load the backend 
            cls._instance._current_environment = None

        return cls._instance


    def initialize_environment(self):
        pass



    def create_environment(self, environment_info: environment_info):

        raise NotImplementedError


    def get_all_environments(self) -> List[str]:
        """
        Get the list of all the environments for this project
        """
        raise NotImplementedError


    def set_current_environment(self, environment_name: str):
        self._load_state()

        self._central_state.current_environment = environment_name

        self._write_state()


    def get_environment(self, environment_name: str) -> Environment:
        raise NotImplementedError


    def get_current_environment_name(self) -> str:
        raise NotImplementedError


    def get_current_environment(self) -> Environment:
        raise NotImplementedError


    def destroy_environment(self, environment_name: str):
        raise NotImplementedError


    def _get_environment_info(self, name: str) -> environment_info:
        self._load_state()

        lookup_dict = {x.name:x for x in self._central_state.environments}

        if not name in lookup_dict:
            raise Exception(f"No environment with name {name}")


        return lookup_dict.get(name)


    
    #################
    ##### Mappers
    #################
    def add_mapper(self, mapper: CloudMapper ) -> None:
        ws = self.get_current_environment().get_workspace()
        ws.add_mapper(mapper)


    def add_mappers(self, mappers: List[CloudMapper] ) -> None:
       ws = self.get_current_environment().get_workspace()
       ws.add_mappers(mappers)


    def get_mappers(self) -> List[CloudMapper]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_mappers()


    def get_mapper_namespace(self) -> Dict:
        ws = self.get_current_environment().get_workspace()
        return ws.get_mapper_namespace()



    #################
    ##### Commands
    #################
    def add_command(self, command_location: str):
        ws = self.get_current_environment().get_workspace()
        ws.add_command(command_location)


    def add_commands(self, command_locations: List[str]):
        ws = self.get_current_environment().get_workspace()
        ws.add_commands(command_locations)

    def get_commands(self) -> List[str]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_commands()


    
    #################
    ##### Components
    #################
    def add_component(self, component: Component):
        ws = self.get_current_environment().get_workspace()
        ws.add_component(component)


    def add_components(self, components: List[Component]):
        ws = self.get_current_environment().get_workspace()
        ws.add_components(components)


    def get_components(self) -> List[Component]:
        ws = self.get_current_environment().get_workspace()
        return ws.get_components()


    def _write_state(self):
        with open(self._state_file_location, 'w') as fh:
            json.dump(self._central_state.dict(), fh, indent=4)


    def _load_state(self) -> project_info:
        with open(self._state_file_location, 'r') as fh:
            self._central_state = project_info(**json.loads(fh))
