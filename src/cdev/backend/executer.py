from os import name
import networkx as nx
from typing import Dict, List

from . import resource_state_manager 

from ..constructs import Cdev_Project, CloudMapper
from ..models import Rendered_State, Component_State_Difference, Action_Type, Resource_State_Difference

from cdev.utils import logger

log = logger.get_cdev_logger(__name__)



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

   
    for component_diff in project_diffs:
        # Creating this resource might require creating a new component in the state so handle that here 
        resource_state_manager.handle_component_difference(component_diff)

        component_name = component_diff.new_component.name

        sorted_resources = generate_sorted_resources(component_diff)

        log.info(f"TOPO SORTED RESOURCE DIFFS: {sorted_resources}")
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
                print(e)




def get_mapper_namespace() -> Dict[str,CloudMapper]:
    # TODO throw error
    return Cdev_Project.instance().get_mapper_namespace()


def generate_sorted_resources(component_diff: Component_State_Difference) -> List[Resource_State_Difference]:
    # nx graphs work on the element level by using the __hash__ of objects added to the graph, and to avoid making every obj support __hash__
    # we are using the id of {x.new_resource.ruuid}::{x.new_resource.hash} to identify resources in the graph then use a dict to map back to 
    # the actual object
    resource_dag = nx.DiGraph()

    
    # build dict from {x.new_resource.ruuid}::{x.new_resource.hash} to resource
    new_resource_id_to_resource_diff = {f"{x.new_resource.ruuid};{x.new_resource.hash}":x for x in component_diff.resource_diffs if x.new_resource }
    

    # this is used as the first check in the translation from parent_references by name
    new_resource_name_to_resource_diff = {f"{x.new_resource.ruuid};{x.new_resource.name}":x for x in component_diff.resource_diffs if x.new_resource }


    # build previous dict from {x.new_resource.ruuid}::{x.new_resource.hash} to resource
    previous_resource_id_to_resource_diff = {f"{x.previous_resource.ruuid};{x.previous_resource.hash}":x for x in component_diff.resource_diffs if not x.new_resource }
    

    # this is used as the first check in the translation from parent_references by name
    previous_resource_name_to_resource_diff = {f"{x.previous_resource.ruuid};{x.previous_resource.name}":x for x in component_diff.resource_diffs if not x.new_resource }

    # We don't want to reference output of diffs that are deletes so do not include the previous diffs
    all_resource_id_to_resource_diff = {}
    all_resource_id_to_resource_diff.update(new_resource_id_to_resource_diff)
    all_resource_id_to_resource_diff.update(previous_resource_id_to_resource_diff)
    

    for resource_diff in component_diff.resource_diffs:
        if resource_diff.new_resource:
            log.info(f"FINDING PARENTS FOR {resource_diff.new_resource.name}")
            log.info(f"PARENTS {resource_diff.new_resource.parent_resources}")
            resource_id = f"{resource_diff.new_resource.ruuid};{resource_diff.new_resource.hash}"
            if resource_diff.new_resource.parent_resources:
                # IF the above resource has parent resources then we need to render their output and make sure this deployment
                # happens after
                resource_dag.add_node(resource_id)

                # A resource can have a parent listed twice via a name and id so need to keep track of the parents we have add already to make sure we don't try to readd
                seen_parents = set()

                for parent_reference in resource_diff.new_resource.parent_resources:
                    # A parent reference can be either ruuid:hash:<hash> or ruuid:name:<name>
                    # if the parent is reference by name means we need to look up the current hash of that parent. 
                    parent_resource_split = parent_reference.split(";")

                    if parent_resource_split[1] == "name":
                        # do lookup by name to get hash
                        name_identifier = f"{parent_resource_split[0]};{parent_resource_split[2]}"
                        if name_identifier in new_resource_name_to_resource_diff:
                            parent_resource = new_resource_name_to_resource_diff.get(name_identifier)

                        else:
                            # If the parent resource in the current diffs then we are assuming that it is already in the state files from a previous deployment
                            # This is a weak assumption, but the current way state is stored there is not a terrific way of finding out if this parent resource
                            # is in the state already from a previous deployment. This error will be caught when doing a look up when trying to deploy the resource.
                            # This also means this ordering only applies to ordering of diffs to make sure they are deployed correctly.
                            continue
                    
                    else:
                        hash_identifier = f"{parent_resource_split[0]};{parent_resource_split[2]}"

                        if hash_identifier in new_resource_id_to_resource_diff:
                            parent_resource = new_resource_id_to_resource_diff.get(hash_identifier)
                        
                        else:
                            # If the parent resource in the current diffs then we are assuming that it is already in the state files from a previous deployment
                            # This is a weak assumption, but the current way state is stored there is not a terrific way of finding out if this parent resource
                            # is in the state already from a previous deployment. This error will be caught when doing a look up when trying to deploy the resource.
                            # This also means this ordering only applies to ordering of diffs to make sure they are deployed correctly.
                            continue
                    


                    parent_resource_id = f"{parent_resource.new_resource.ruuid};{parent_resource.new_resource.hash}"
                    
                    if parent_resource_id in seen_parents:
                        log.debug(f"Already seen parent {parent_resource_id} for {resource_diff.new_resource.name}; {seen_parents}")
                        continue

                    log.info(f"PARENT RESOURCE {parent_resource_id} for {resource_diff.new_resource.name}")
                    # IF the parent is in the diff make this resource a descandant in the DAG
                    resource_dag.add_node(parent_resource_id)
                    resource_dag.add_edge(parent_resource_id, resource_id)
                    seen_parents.add(parent_resource_id)
        
            else:
                # IF this resource has no parents then add it as a top level resource in the DAG
                resource_dag.add_node(resource_id)
        
        else:
            # IF no new resource then this is a delete then we need to find any parents that are also being delete. Since these are delete, we want to delete
            # parents after the resource so change the direction of the connection in the dag

            resource_id = f"{resource_diff.previous_resource.ruuid};{resource_diff.previous_resource.hash}"

            if resource_diff.previous_resource.parent_resources:
                # IF the above resource has parent resources then we need to render their output and make sure this deployment
                # happens after
                resource_dag.add_node(resource_id)

                # A resource can have a parent listed twice via a name and id so need to keep track of the parents we have add already to make sure we don't try to readd
                seen_parents = set()

                for parent_reference in resource_diff.previous_resource.parent_resources:                
                    # A parent reference can be either ruuid:hash:<hash> or ruuid:name:<name>
                    # if the parent is reference by name means we need to look up the current hash of that parent. 
                    parent_resource_split = parent_reference.split(";")

                    if parent_resource_split[1] == "name":
                        # do lookup by name to get hash
                        name_identifier = f"{parent_resource_split[0]};{parent_resource_split[2]}"
                        if name_identifier in previous_resource_name_to_resource_diff:
                            parent_resource = previous_resource_name_to_resource_diff.get(name_identifier)

                        else:
                            # If the parent resource in the current diffs then we are assuming that it is already in the state files from a previous deployment
                            # This is a weak assumption, but the current way state is stored there is not a terrific way of finding out if this parent resource
                            # is in the state already from a previous deployment. This error will be caught when doing a look up when trying to deploy the resource.
                            # This also means this ordering only applies to ordering of diffs to make sure they are deployed correctly.
                            continue
                    
                    else:
                        hash_identifier = f"{parent_resource_split[0]};{parent_resource_split[2]}"

                        if hash_identifier in previous_resource_id_to_resource_diff:
                            parent_resource = previous_resource_id_to_resource_diff.get(hash_identifier)
                        
                        else:
                            # If the parent resource in the current diffs then we are assuming that it is already in the state files from a previous deployment
                            # This is a weak assumption, but the current way state is stored there is not a terrific way of finding out if this parent resource
                            # is in the state already from a previous deployment. This error will be caught when doing a look up when trying to deploy the resource.
                            # This also means this ordering only applies to ordering of diffs to make sure they are deployed correctly.
                            continue
                    


                    parent_resource_id = f"{parent_resource.previous_resource.ruuid};{parent_resource.previous_resource.hash}"
                    
                    if parent_resource_id in seen_parents:
                        log.debug(f"Already seen parent {parent_resource_id} for {resource_diff.previous_resource.name}; {seen_parents}")
                        continue

                    log.info(f"PARENT RESOURCE {parent_resource_id} for {resource_diff.previous_resource.name}")
                    # IF the parent is in the diff make this resource a descandant in the DAG
                    resource_dag.add_node(parent_resource_id)
                    resource_dag.add_edge(resource_id, parent_resource_id)
                    seen_parents.add(parent_resource_id)
            else:
                resource_dag.add_node(resource_id)
                log.info(f"ADDING {resource_id} AS DELETE")

    sorted_resources = []
    resource_dag_list = list(nx.topological_sort(resource_dag))
    for resource_id in resource_dag_list:
        sorted_resources.append(all_resource_id_to_resource_diff.get(resource_id))

    return sorted_resources
