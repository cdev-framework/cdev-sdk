from core.utils import topological_helper

from ..sample_data import simple_resources_for_find_parents, simple_differences_for_topo_sort


def test_find_parents():
    resources_and_outputs = simple_resources_for_find_parents()

    for resource, output_length in resources_and_outputs:
        rv = topological_helper.find_parents(resource)

        assert len(rv) == output_length



def test_sort_changes():
    """
    Test the topological helper sorting of the changes into a DAG that can be used to deploy the changes. It should check that all the nodes and edges in the returned graph are correct.
    """
    changes, correct_edges, correct_nodes = simple_differences_for_topo_sort()


    dag = topological_helper.generate_sorted_resources(changes)

    # Check that all nodes from created dag are correct
    if not len(dag.nodes()) == len(correct_nodes):
        print(f"returned {len(dag.nodes())} and should have had {len(correct_nodes)} nodes")
        assert False

    for rv_node in dag.nodes():
        if not rv_node in correct_nodes:
            # Returned edge not in correct edges
            print(rv_node)
            assert False

        correct_nodes.remove(rv_node)


    if correct_nodes:
        print(correct_nodes)
        # There should not be any remaining edges
        assert False
    

    # Check that all edges from created dag are correct
    if not len(dag.edges()) == len(correct_edges):
        print(f"returned {len(dag.edges())} and should have had {len(correct_edges)} edges")
        assert False


    for rv_edge in dag.edges():
        if not rv_edge in correct_edges:
            # Returned edge not in correct edges
            print(rv_edge)
            assert False

        correct_edges.remove(rv_edge)


    if correct_edges:
        print(correct_edges)
        # There should not be any remaining edges
        assert False

