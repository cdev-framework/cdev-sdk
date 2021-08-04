import networkx as nx
from typing import Dict, List

from . import resource_state_manager 

from ..constructs import Cdev_Project, CloudMapper
from ..models import Rendered_State, Component_State_Difference, Action_Type





def validate_diffs(project_diffs: List[Component_State_Difference]) -> bool:

    return True


def deploy_diffs(project_diffs: List[Component_State_Difference]) -> None:
    """
    This function is used to deploy the differences found within the current project and previous deployed state

    Since the resources in the differences can have un-rendered output variables, we need to first order the desired
    changes in a DAG so that they can then be TOPO sorted into an order that allows for deployment. From this TOPO sorted
    list of diffs, we deploy each resource individually then update the project state after each deployment.

    The deployment of the resources is handled by a mapper. Mappers register themselves with top-level namespaces that resources 
    have. These namespaces are used to determine which mapper deploys which resource. 


    """
    
    mapper_namespace = get_mapper_namespace()

    resource_dag = nx.DiGraph()
   
    for diff in project_diffs:
        # Creating this resource might require creating a new component in the state so handle that here 
        resource_state_manager.handle_component_difference(diff)

        component_name = diff.new_component.name
        # nx graphs work on the element level by using the __hash__ of objects added to the graph, and to avoid making every obj support __hash__
        # we are using the id of {x.new_resource.ruuid}::{x.new_resource.hash} to identify resources in the graph then use a dict to map back to 
        # the actual object
        resource_dag = nx.DiGraph()

        # build dict from {x.new_resource.ruuid}::{x.new_resource.hash} to resource
        resource_id_to_resource_diff = {f"{x.new_resource.ruuid}::{x.new_resource.hash}":x for x in diff.resource_diffs if x.new_resource }
        resource_id_to_resource_diff.update({f"{x.previous_resource.ruuid}::{x.previous_resource.hash}":x for x in diff.resource_diffs if not x.new_resource })
        
        for resource_diff in diff.resource_diffs:
            if resource_diff.new_resource:
                resource_id = f"{resource_diff.new_resource.ruuid}::{resource_diff.new_resource.hash}"
                if resource_diff.new_resource.parent_resources:
                    # IF the above resource has parent resources then we need to render their output and make sure this deployment
                    # happens after
                    resource_dag.add_node(resource_id)

                    for parent in resource_diff.new_resource.parent_resources:
                        if not parent in resource_id_to_resource_diff:
                            # The parent is not being changed and therefor already rendered and the output in the Cloud Mapping
                            # TODO add check to make sure resource actually exists
                            continue

                        # IF the parent is in the diff make this resource a descandant in the DAG
                        resource_dag.add_node(parent)
                        resource_dag.add_edge(parent, resource_id)
            
                else:
                    # IF this resource has no parents then add it as a top level resource in the DAG
                    resource_dag.add_node(resource_id)
            
            else:
                # IF no new resource then this is a delete and should be added to the end of the TOPO sort because previous values might depend
                # on it
                resource_id = f"{resource_diff.previous_resource.ruuid}::{resource_diff.previous_resource.hash}"
                resource_dag.add_node(resource_id)
                
        
        sorted_resources = []
        resource_dag_list = list(nx.topological_sort(resource_dag))
        for resource_id in resource_dag_list:
            sorted_resources.append(resource_id_to_resource_diff.get(resource_id))


        for resource_diff in sorted_resources:
            try:
                # Get the top level namespace of this resource
                if resource_diff.new_resource:
                    namespace = resource_diff.new_resource.ruuid.split("::")[0]
                else:
                    namespace = resource_diff.previous_resource.ruuid.split("::")[0]


                if namespace in mapper_namespace:
                    # Have the assigned mapper render any output variables before passing to deployer
                    output_rendered_resource = mapper_namespace[namespace].render_resource_outputs(resource_diff)
                    # Deploy the resource
                    # TODO catch some errors
                    did_deploy = mapper_namespace[namespace].deploy_resource(output_rendered_resource)
                    #did_deploy = True
                    if did_deploy:
                        # Update the resource state to reflect that we successfully deployed the cloud resources
                        resource_state_manager.write_resource_difference(component_name,resource_diff)
                    else:
                        print(f"COULD NOT COMPLETE {resource_diff}")
                else:
                    print("REALLY BAD")

            except Exception as e:
                print("EXCEPT HERE")
                print("FOUND IITTT")
                print(e)




def get_mapper_namespace() -> Dict[str,CloudMapper]:
    # TODO throw error
    return Cdev_Project.instance().get_mapper_namespace()

