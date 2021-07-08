from typing import Dict, List

from . import resource_state_manager 

from ..constructs import Cdev_Project
from ..models import Rendered_State, Component_State_Difference, Action_Type



def create_diffs(rendered_frontend: Rendered_State) -> List[Component_State_Difference]:
    
    project_diffs = resource_state_manager.create_project_diffs(rendered_frontend)
    #print(project_diffs)

    mapper_namespace = get_mapper_namespace()
    print(mapper_namespace)
    
    for diff in project_diffs:
        resource_state_manager.write_component_difference(diff)



def get_mapper_namespace() -> Dict:
    # TODO throw error
    return Cdev_Project.instance().get_mapper_namespace()

