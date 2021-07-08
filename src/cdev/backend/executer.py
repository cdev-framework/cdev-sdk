from typing import Dict, List

from . import resource_state_manager 
from .models import Component_State_Difference, Action_Type

from cdev.models import Rendered_State


def create_diffs(rendered_frontend: Rendered_State) -> List[Component_State_Difference]:
    
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    #print(project_diffs)
    
    for diff in project_diffs:
        print("----------")
        print(diff)
        print("------------")
        resource_state_manager.write_component_difference(diff)



def initialize_providers() -> Dict:
    pass

