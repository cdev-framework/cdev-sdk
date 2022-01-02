from typing import Dict, List, Tuple

from core.constructs.resource import Cloud_Output, Resource_Change_Type, Resource_Reference_Change_Type, ResourceModel, Resource_Difference, Resource_Reference_Difference
from core.constructs.components import Component_Change_Type, Component_Difference
import networkx as nx



deliminator = '+'

def find_parents(resource: ResourceModel) -> List[Cloud_Output]:
    
    resource_as_obj = resource.dict()

    cloud_outputs = find_cloud_output(resource_as_obj)

    return cloud_outputs


def find_cloud_output(obj: dict) -> List[Cloud_Output]:

    rv = _recursive_replace_output(obj)

    return rv


def _recursive_replace_output(obj) -> List[Cloud_Output]:
    rv = []

    if isinstance(obj, dict): 
        for k,v in obj.items():
            if isinstance(v, dict):
                if "_id" in v and v.get("_id") == 'cdev_output':
                    rv.append(Cloud_Output(**v))
                else:
                    rv.extend(_recursive_replace_output(v))

            elif isinstance(v, list):
                all_items_rendered = [_recursive_replace_output(x) for x in v]
                
                for item in all_items_rendered:
                    rv.extend(item)

        return rv

    elif isinstance(obj, list):
        all_items_rendered = [_recursive_replace_output(x) for x in obj]
                
        for item in all_items_rendered:
            rv.extend(item)

    return rv


def generate_sorted_resources(differences: Tuple[List[Component_Difference], List[Resource_Difference], List[Resource_Reference_Difference]]) -> nx.DiGraph:
    # nx graphs work on the element level by using the __hash__ of objects added to the graph, and to avoid making every obj support __hash__
    # we are using the id of {x.new_resource.ruuid}::{x.new_resource.hash} to identify resources in the graph then use a dict to map back to 
    # the actual object
    change_dag = nx.DiGraph()


    component_differences = differences[0]
    resource_differences = differences[1]
    reference_differences = differences[2]
    

    
    component_ids = {_create_component_id(x.new_name):x for x in component_differences if x.action_type == Component_Change_Type.CREATE or x.action_type == Component_Change_Type.UPDATE_NAME or x.action_type == Component_Change_Type.UPDATE_IDENTITY}
    component_ids.update({_create_component_id(x.previous_name):x for x in component_differences if x.action_type == Component_Change_Type.DELETE})

    
    resource_ids = {_create_resource_id(x.component_name, x.new_resource.ruuid, x.new_resource.name):x for x in resource_differences if x.action_type == Resource_Change_Type.UPDATE_IDENTITY or x.action_type == Resource_Change_Type.CREATE or x.action_type == Resource_Change_Type.UPDATE_NAME}
    resource_ids.update({_create_resource_id(x.component_name, x.previous_resource.ruuid, x.previous_resource.name):x for x in resource_differences if x.action_type == Resource_Change_Type.DELETE})

    
    reference_ids = {_create_reference_id(x.originating_component_name, x.resource_reference.component_name, x.resource_reference.ruuid, x.resource_reference.name):x for x in reference_differences}

    
    for component_id, component in component_ids.items():
        change_dag.add_node(component)


    for resource_id, resource in resource_ids.items():
        change_dag.add_node(resource)

        component_id = _create_component_id(resource.component_name)

        if component_id in component_ids:
            change_dag.add_edge(component_ids.get(component_id), resource)

        else:
            raise Exception(f"There should always be a change in a component for a resource change {resource}")

        parent_cloudoutputs = find_parents(resource.new_resource) if not resource.action_type == Resource_Change_Type.DELETE else find_parents(resource.previous_resource)


        if not parent_cloudoutputs:
            continue

        for parent_cloudoutput in parent_cloudoutputs:
            # Parent resources must be in the same component
            if parent_cloudoutput.type == 'resource':
                # Cloud outputs of a resource will always be from the same component
                parent_resource_id = _create_resource_id( resource.component_name, parent_cloudoutput.ruuid, parent_cloudoutput.name)

                if parent_resource_id in resource_ids:
                    if resource_ids.get(parent_resource_id).action_type == Resource_Change_Type.DELETE:
                        raise Exception(f"Attemping to use output of Resource that is going to be deleted {resource} {parent_cloudoutput}")

                    # Make this resource change a child of the parent resource change
                    change_dag.add_edge(resource_ids.get(parent_resource_id), resource)

            elif parent_cloudoutput.type == 'reference':
                parent_reference_id = _create_reference_id(resource.component_name, parent_cloudoutput.component_name, parent_cloudoutput.ruuid, parent_cloudoutput.name)

                if parent_reference_id in reference_ids:
                    if reference_ids.get(parent_reference_id).action_type == Resource_Reference_Change_Type.DELETE:
                        raise Exception(f"Attempting to use output of a Reference that is going to be deleted {resource} {parent_cloudoutput}")

                    change_dag.add_edge(resource_ids.get(parent_reference_id), resource)

    for reference_id, reference in reference_ids.items():
        change_dag.add_node(reference)

        resource_id = _create_resource_id(reference.resource_reference.component_name, reference.resource_reference.ruuid, reference.resource_reference.name)
        if resource_id in resource_ids:
            # If there is also a change to the component this reference is apart of then the changes need to be ordered
            if reference.action_type == Resource_Reference_Change_Type.CREATE:
                if resource_ids.get(resource_id).action_type == Resource_Change_Type.DELETE:
                    # We can not create a reference if that resource is currently being destroyed.
                    raise Exception(f"Trying to reference a resource that is being deleted {reference} -> {resource_id}")


                # Since the reference is being created, we should perform the operation after the changes to the underlying resource 
                change_dag.add_edge(resource_ids.get(resource_id), reference)

            else:
                change_dag.add_edge(reference, resource_ids.get(resource_id))

        else:
            # Since the original resource is not in the change set, it should be checked to be sure that it is accessible from the backend
            pass
            

    return change_dag


def _create_component_id(component_name: str ) -> str:
    # Component Differences will be identified by the key component<deliminator><component_name>
    return f'component{deliminator}{component_name}'


def _create_resource_id(component_name: str, ruuid: str, name: str) -> str:
    # Resource Differences will be identified by the key resource<deliminator><ruuid><deliminator><name>
    return f'resource{deliminator}{component_name}{deliminator}{ruuid}{deliminator}{name}'


def _create_reference_id(originating_component_name: str, component_name: str, ruuid: str, name: str) -> str:
    # Reference Differences will be identified by the key reference<deliminator><ruuid><deliminator><name>
    return f'reference{deliminator}{originating_component_name}{deliminator}{component_name}{deliminator}{ruuid}{deliminator}{name}'
