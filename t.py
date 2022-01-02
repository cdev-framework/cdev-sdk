from concurrent.futures import ThreadPoolExecutor, Future
from enum import Enum
from networkx.classes.digraph import DiGraph
from networkx.classes.reportviews import NodeView
from tests.core.sample_data import simple_differences_for_topo_sort
from typing import Dict, Callable
from time import sleep

from src.core.utils.topological_resource_sort import generate_sorted_resources

import networkx as nx



resources = generate_sorted_resources(simple_differences_for_topo_sort())


class node_state(str, Enum):
    UNPROCESSED = "UNPROCESSED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"
    PARENT_ERROR = "PARENT_ERROR"

    

def proccess_node(node: NodeView):

    print(f"Starting Process ({type(node)}) {node}")
    sleep(1)
    
    print(f"Finished Process ({type(node)}) {node}")



def topological_iteration(dag: DiGraph, process: Callable[[NodeView], None], thread_count: int = 1, interval: float = .3):
    """Execute a given process over a DAG in a threaded way. 

    Args:
        dag (DiGraph): [description]
        thread_count (int, optional): [description]. Defaults to 1.
        interval (float, optional): [description]. Defaults to .3.
    """
    
    all_children = set(x[1] for x in resources.edges)
    all_nodes = set(x for x in resources.nodes())

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
        print(f"loop")
        

    print("---------done-----------------")
    print(_node_to_state)
    print(_processing_future_to_resource)

    executor.shutdown()


def _recursively_mark_parent_failure(_node_to_state: Dict[NodeView,node_state], dag: DiGraph, parent_node: NodeView) -> None:

    if parent_node not in _node_to_state:
        raise Exception(f"trying to mark node ({parent_node}) but cant not find it in given dict")

    
    children = dag.successors(parent_node)

    for child in children:

        if child not in _node_to_state:
            raise Exception(f"trying to mark node ({child}) but cant not find it in given dict")
        
        _node_to_state[child] = node_state.PARENT_ERROR
        print(f"Wont process {child} because parent failed")

        _recursively_mark_parent_failure(_node_to_state, dag, child)

        

        



topological_iteration(resources, proccess_node)

