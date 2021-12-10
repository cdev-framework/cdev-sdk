from core.constructs.resource import Cloud_Output, ResourceModel
import pytest
from typing import Dict, List, Tuple

from core.constructs.backend import Backend

from . import sample_data


def simple_actions(test_backend: Backend):
    """
    Create a single component and add some resources. Then delete the resources and 
    component.
    """
    resource_state_name = "demo_state"
    component_name = "demo_component"
    final_state = sample_data.simple_create_resource_changes(component_name)
    sample_delete_resource_changes = sample_data.simple_delete_resource_changes(component_name)

    resource_state_uuid = _create_simple_resource_state_and_component(test_backend,  resource_state_name, component_name)
    # Create a resource change then automatically complete the transaction
    for resource_change in final_state:
        tmp_transaction = test_backend.create_resource_change(
                                resource_state_uuid, 
                                component_name, 
                                resource_change
                            )

        # no cloud output
        test_backend.complete_resource_change(
            resource_state_uuid,
            component_name,
            resource_change, 
            tmp_transaction, 
            {}
        )


    returned_component = test_backend.get_component(resource_state_uuid, component_name)

    assert len(final_state) == len(returned_component.resources)
    
    # Try deleting a component that still has resources
    with pytest.raises(Exception):
        test_backend.delete_component(resource_state_uuid, component_name)

    # Delete resources
    for resource_change in sample_delete_resource_changes:
        tmp_transaction = test_backend.create_resource_change(
                                resource_state_uuid, 
                                component_name, 
                                resource_change
                            )

        test_backend.complete_resource_change(
            resource_state_uuid,
            component_name,
            resource_change, 
            tmp_transaction, 
            {}
        )


    returned_component = test_backend.get_component(resource_state_uuid, component_name)

    assert 0 == len(returned_component.resources)

    with pytest.raises(Exception):
        test_backend.delete_resource_state(resource_state_uuid)

    test_backend.delete_component(resource_state_uuid, component_name)

    # Get an error when trying to access the component
    with pytest.raises(Exception):
        test_backend.get_component(resource_state_uuid, component_name)


    test_backend.delete_resource_state(resource_state_uuid)


    # Test that the resource state was added as a top level resource state
    assert 0 == len(test_backend.get_top_level_resource_states())


def simple_get_resource(test_backend: Backend):
    """
    Add some resource to the state and then check that they were properly added
    """
    resource_state_name = "demo_state"
    component_name = "demo_component"
    final_state = sample_data.simple_create_resource_change_with_output(component_name)
    

    resource_state_uuid = _create_simple_resource_state_and_component(test_backend, resource_state_name, component_name)


    # Create a resource change then automatically complete the transaction
    for resource_change, cloud_output in final_state:
        tmp_transaction = test_backend.create_resource_change(
                                resource_state_uuid, 
                                component_name, 
                                resource_change
                            )

        test_backend.complete_resource_change(
            resource_state_uuid,
            component_name,
            resource_change, 
            tmp_transaction, 
            cloud_output
        )

    

    desired_final_state = [(resource_change.new_resource, original_output, "arn") for resource_change, original_output in final_state]

    _check_final_resources_and_output(test_backend, resource_state_uuid, component_name, desired_final_state)
    


def _create_simple_resource_state_and_component(
        test_backend: Backend, 
        resource_state_name: str, 
        component_name: str
    ):
    """
    Create resource state with a single empty component
    """
    # All create resources
    resource_state_uuid = test_backend.create_resource_state(resource_state_name, None)

    # Test that the resource state was added as a top level resource state
    assert resource_state_uuid == test_backend.get_resource_state(resource_state_uuid).uuid


    test_backend.create_component(resource_state_uuid, component_name)

    returned_component = test_backend.get_component(resource_state_uuid, component_name)

    # Test we can get the component correctly
    assert component_name == returned_component.name

    return resource_state_uuid


def _check_final_resources_and_output(test_backend: Backend, resource_state_uuid: str, component_name: str, final_state: List[Tuple[ResourceModel, Dict, str]]):
    # Assert:
    #   All resources names are there
    #   All resources can be accessed by name
    #   All resources can be accessed by hash
    #   All cloud outputs can be access by name
    #   All cloud outputs can be access by hash

    returned_component = test_backend.get_component(resource_state_uuid, component_name)

    resource_names = set(x.name for x in returned_component.resources)
    
    assert all((resource.name in resource_names) for resource, _, _ in final_state)
    assert all((resource == test_backend.get_resource_by_name(resource_state_uuid, component_name, resource.ruuid, resource.name)) for resource, _, _ in final_state)
    assert all((resource == test_backend.get_resource_by_hash(resource_state_uuid, component_name, resource.ruuid, resource.hash)) for resource, _, _ in final_state)
    assert all((original_output.get(key) == test_backend.get_cloud_output_value_by_name(resource_state_uuid, component_name, resource.ruuid, resource.name, key)) for resource, original_output, key in final_state)
    assert all((original_output.get(key) == test_backend.get_cloud_output_value_by_hash(resource_state_uuid, component_name, resource.ruuid, resource.hash, key)) for resource, original_output, key in final_state)