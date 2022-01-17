from core.utils import topological_helper

from ..sample_data import simple_resources_for_find_parents, simple_differences_for_topo_sort


def test_find_parents():
    resources_and_outputs = simple_resources_for_find_parents()

    for resource, output_length in resources_and_outputs:
        rv = topological_helper.find_parents(resource)

        assert len(rv) == output_length



def test_sort_changes():
    changes, correct_edges = simple_differences_for_topo_sort()


    dag = topological_helper.generate_sorted_resources(changes)

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

