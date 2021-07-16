import networkx as nx
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
    
    mapper_namespace = get_mapper_namespace()

    resource_dag = nx.DiGraph()
    top_level_resources = []
   

    for diff in project_diffs:
        component_name = diff.new_component.name
        resource_state_manager.handle_component_difference(diff)


        resource_dag = nx.DiGraph()
        top_level_resources = []
        resource_id_to_resource_diff = {f"{x.new_resource.ruuid}::{x.new_resource.hash}":x for x in diff.resource_diffs if x.new_resource }
        
        print(resource_id_to_resource_diff)
        for resource_diff in diff.resource_diffs:
            resource_id = f"{resource_diff.new_resource.ruuid}::{resource_diff.new_resource.hash}"

            if resource_diff.new_resource:
                if resource_diff.new_resource.parent_resources:
                    
                    resource_dag.add_node(resource_id)

                    for parent in resource_diff.new_resource.parent_resources:
                        if not parent in resource_id_to_resource_diff:
                            print(f"{parent} -> NO NEED this parent must not be changing")
                            continue

                        resource_dag.add_node(parent)
                        resource_dag.add_edge(parent, resource_id)

                    continue
            
                else:
                    resource_dag.add_node(resource_id)
            
            else:
                resource_dag.add_node(resource_id)
                
        
        sorted_resources = []
        resource_dag_list = list(nx.topological_sort(resource_dag))
        for resource_id in resource_dag_list:
            sorted_resources.append(resource_id_to_resource_diff.get(resource_id))


        for resource_diff in sorted_resources:
            try:
                if resource_diff.new_resource:
                    mapper = resource_diff.new_resource.ruuid.split("::")[0]
                else:
                    mapper = resource_diff.previous_resource.ruuid.split("::")[0]


                if mapper in mapper_namespace:
                    ouput_rendered_resource = render_resource_outputs(resource_diff)
                    did_deploy = mapper_namespace[mapper].deploy_resource(ouput_rendered_resource)
                    if did_deploy:
                        resource_state_manager.write_resource_difference(component_name,resource_diff)
                else:
                    print("REALLY BAD")

            except Exception as e:
                print("EXCEPT HERE")
                print(e)



def render_resource_outputs(resourse_diff):
    return resourse_diff


                



def get_mapper_namespace() -> Dict[str,CloudMapper]:
    # TODO throw error
    return Cdev_Project.instance().get_mapper_namespace()

