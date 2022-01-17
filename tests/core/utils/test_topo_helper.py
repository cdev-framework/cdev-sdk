from core.utils import topological_helper

from ..sample_data import simple_resources_for_find_parents


def test_find_parents():
    resources_and_outputs = simple_resources_for_find_parents()

    for resource, output_length in resources_and_outputs:
        rv = topological_helper.find_parents(resource)
        
        assert len(rv) == output_length
