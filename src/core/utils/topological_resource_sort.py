from concurrent.futures import ThreadPoolExecutor, Future
from enum import Enum
from networkx.classes.digraph import DiGraph
from networkx.classes.reportviews import NodeView


from typing import Callable, Dict, List, Tuple
from time import sleep

from core.constructs.resource import Cloud_Output, Resource_Change_Type, Resource_Reference_Change_Type, ResourceModel, Resource_Difference, Resource_Reference_Difference
from core.constructs.components import Component_Change_Type, Component_Difference



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


def generate_sorted_resources(differences: Tuple[List[Component_Difference], List[Resource_Difference], List[Resource_Reference_Difference]]) -> DiGraph:
    # nx graphs work on the element level by using the __hash__ of objects added to the graph, so all the elements added to the graph should be a pydantic Model with
    # the 'frozen' feature set
    change_dag = DiGraph()


    component_differences = differences[0]
    resource_differences = differences[1]
    reference_differences = differences[2]
    

    
    component_ids = {_create_component_id(x.new_name):x for x in component_differences if x.action_type == Component_Change_Type.CREATE or x.action_type == Component_Change_Type.UPDATE_NAME or x.action_type == Component_Change_Type.UPDATE_IDENTITY}
    component_ids.update({_create_component_id(x.previous_name):x for x in component_differences if x.action_type == Component_Change_Type.DELETE})

    
    resource_ids = {_create_resource_id(x.component_name, x.new_resource.ruuid, x.new_resource.name):x for x in resource_differences if x.action_type == Resource_Change_Type.UPDATE_IDENTITY or x.action_type == Resource_Change_Type.CREATE or x.action_type == Resource_Change_Type.UPDATE_NAME}
    resource_ids.update({_create_resource_id(x.component_name, x.previous_resource.ruuid, x.previous_resource.name):x for x in resource_differences if x.action_type == Resource_Change_Type.DELETE})

    
    reference_ids = {_create_reference_id(x.originating_component_name, x.resource_reference.component_name, x.resource_reference.ruuid, x.resource_reference.name):x for x in reference_differences}

    
    for _, component in component_ids.items():
        change_dag.add_node(component)


    for _, resource in resource_ids.items():
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

    for _, reference in reference_ids.items():
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



class node_state(str, Enum):
    UNPROCESSED = "UNPROCESSED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"
    PARENT_ERROR = "PARENT_ERROR"



    
def topological_iteration(dag: DiGraph, process: Callable[[NodeView], None], thread_count: int = 1, interval: float = .3):
    """
    Execute a given process over a DAG in a threaded way. 

    Args:
        dag (DiGraph): [description]
        thread_count (int, optional): [description]. Defaults to 1.
        interval (float, optional): [description]. Defaults to .3.
    """
    
    all_children = set(x[1] for x in dag.edges)
    all_nodes = set(x for x in dag.nodes())

    starting_nodes = all_nodes - all_children

    nodes_to_process: list[NodeView] = []
    nodes_to_process.extend(starting_nodes)

    _processing_future_to_resource: Dict[Future, NodeView] = {}
    _node_to_state: Dict[NodeView,node_state] = {x:node_state.UNPROCESSED for x in all_children}

    executor = ThreadPoolExecutor(thread_count)
    
    while any(_node_to_state.get(x) == node_state.UNPROCESSED or _node_to_state.get(x) == node_state.PROCESSING for x in all_nodes):
        
        # Pull any ready nodes to be processed and add them to the thread pool
        for _ in range(0,len(nodes_to_process)):
            node_to_process = nodes_to_process.pop(0)

            future = executor.submit(process, (node_to_process))

            _processing_future_to_resource[future] = node_to_process
            _node_to_state[node_to_process] = node_state.PROCESSING

        
        # Check if any of the futures are finished and then make decisions about their children from the rv of the future
        for fut, node in _processing_future_to_resource.copy().items():
            # Note python throws runtime error if you change a dict size while iterating so use a copy for now.
            # TODO: Check if there is a more optimized way to do this

            if not fut.done():
                # Still processing
                continue


            try:
                result = fut.result()

                # No exceptions raised so process completed correctly
                _node_to_state[node] = node_state.PROCESSED

                children = dag.successors(node)

                for child in children:
                    # If any of the parents of the child has not been processed this node is not ready
                    if any(not _node_to_state.get(x) == node_state.PROCESSED for x in dag.predecessors(child)):
                        continue
                    
                    nodes_to_process.append(child)

            except Exception as e:
                # Since this returned a error need to mark all children as unable to deploy
                print(e)

                _node_to_state[node] = node_state.ERROR
                print(f"FAILED {node}")

                # mark an descdents of this node as unable to process
                _recursively_mark_parent_failure(_node_to_state, dag, node)

                

            # Remove the future from the dictionary
            _processing_future_to_resource.pop(fut)

        sleep(interval)


    executor.shutdown()


def _recursively_mark_parent_failure(_node_to_state: Dict[NodeView, node_state], dag: DiGraph, parent_node: NodeView) -> None:

    if parent_node not in _node_to_state:
        raise Exception(f"trying to mark node ({parent_node}) but cant not find it in given dict")

    
    children = dag.successors(parent_node)

    for child in children:

        if child not in _node_to_state:
            raise Exception(f"trying to mark node ({child}) but cant not find it in given dict")
        
        _node_to_state[child] = node_state.PARENT_ERROR

        _recursively_mark_parent_failure(_node_to_state, dag, child)
