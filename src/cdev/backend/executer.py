from typing import Dict, List

from . import resource_state_manager 

from ..constructs import Cdev_Project, CloudMapper
from ..models import Rendered_State, Component_State_Difference, Action_Type




def validate_diffs(project_diffs: List[Component_State_Difference]) -> bool:

    return True


def deploy_diffs(project_diffs: List[Component_State_Difference]) -> None:
    
    # This is the return value that will be used in the next step to deploy actualt cloud resources
    # It is important to buffer all these request before actual making them because we can then do
    # basic syntax checks and other integrity confirmations before actually creating the resources.
    mapper_to_resource_diffs = {}
    for diff in project_diffs:
        resource_state_manager.handle_component_difference(diff)
        for resource_diff in diff.resource_diffs:
            if resource_diff.new_resource:
                print("WHY HERE")
                provider_namespace = resource_diff.new_resource.ruuid.split("::")[0]
            else:
                provider_namespace = resource_diff.previous_resource.ruuid.split("::")[0]
                

            if provider_namespace in mapper_to_resource_diffs:
                mapper_to_resource_diffs[provider_namespace].append((diff.new_component.name,resource_diff))
            else:
                mapper_to_resource_diffs[provider_namespace] = [(diff.new_component.name, resource_diff)]



    mapper_namespace = get_mapper_namespace()
    for mapper in mapper_to_resource_diffs:
        if mapper not in mapper_namespace:
            print("REALLLY BAD")
            # TODO throw error
        for resource_diff in mapper_to_resource_diffs.get(mapper):
            try:
                did_deploy = mapper_namespace[mapper].deploy_resource(resource_diff[0], resource_diff[1])

                if did_deploy:
                    resource_state_manager.write_resource_difference(resource_diff[0], resource_diff[1])

            except Exception as e:
                print(e)




                



def get_mapper_namespace() -> Dict[str,CloudMapper]:
    # TODO throw error
    return Cdev_Project.instance().get_mapper_namespace()

