from networkx.classes.digraph import DiGraph
from networkx.classes.reportviews import NodeView
from tests.core.sample_data import simple_differences_for_topo_sort

from src.core.utils.topological_resource_sort import generate_sorted_resources

import networkx as nx



resources = generate_sorted_resources(simple_differences_for_topo_sort())




def dfs_iteration(dag: DiGraph):
    
    all_children = set(x[1] for x in resources.edges)

    all_nodes = set(x for x in resources.nodes())

    starting_nodes = all_nodes - all_children

    nodes_to_process: list[NodeView] = []
    processed_nodes = set()

    nodes_to_process.extend(starting_nodes)

    while nodes_to_process:
        node = nodes_to_process.pop(0)
        proccess_node(node)
        processed_nodes.add(node)

        children = dag.successors(node)

        for child in children:
            # If any of the parents of the child has not been processed this node is not ready
            if any(not x in processed_nodes for x in dag.predecessors(child)):
                continue

            nodes_to_process.insert(0, child)

        



def proccess_node(node):
    print(f"({type(node)}) {node}")


dfs_iteration(resources)

