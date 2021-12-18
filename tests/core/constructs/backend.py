from core.constructs import backend
from core.constructs.resource import Cloud_Output, Resource_Change_Type, Resource_Difference, ResourceModel
import pytest
from typing import Dict, List, Tuple

from core.constructs.backend import Backend
from core.constructs.backend_exceptions import *

from . import sample_data

################################
##### Simple Tests
################################

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


################################
#### Simple Failure Tests
################################

def conflicting_names_resource_state(test_backend: Backend):
    """
    Create a single component and add some resources. Then delete the resources and 
    component.
    """
    resource_state_name = "demo_state"
    component_name = "demo_component"

    _create_simple_resource_state_and_component(test_backend,  resource_state_name, component_name)
    
    with pytest.raises(ResourceStateAlreadyExists):
        _create_simple_resource_state_and_component(test_backend,  resource_state_name, component_name)


def conflicting_names_component(test_backend: Backend):
    """
    Create a single component and add some resources. Then delete the resources and 
    component.
    """
    resource_state_name = "demo_state"
    component_name = "demo_component"

    resource_state_uuid = _create_simple_resource_state_and_component(test_backend,  resource_state_name, component_name)
    
    with pytest.raises(ComponentAlreadyExists):
        test_backend.create_component(resource_state_uuid, component_name)


def get_missing_component(test_backend: Backend):
    resource_state_name = "demo_state"
    component_name = "demo_component"

    resource_state_uuid = _create_simple_resource_state_and_component(test_backend,  resource_state_name, component_name)

    test_backend.delete_component(resource_state_uuid, component_name)

    with pytest.raises(ComponentDoesNotExist):
        test_backend.get_component(resource_state_uuid, component_name)


def get_missing_resource(test_backend: Backend):
    resource_state_name = "demo_state"
    component_name = "demo_component"
    
    resource_state_uuid = _create_simple_resource_state_and_component(test_backend,  resource_state_name, component_name)
    # Create a resource change then automatically complete the transaction
    
    with pytest.raises(ResourceDoesNotExist):
        test_backend.get_resource_by_name(resource_state_uuid, component_name, "cdev::resource", "demo_name")


    with pytest.raises(ResourceDoesNotExist):
        test_backend.get_resource_by_hash(resource_state_uuid, component_name, "cdev::resource", "1 ")


def get_missing_cloud_output(test_backend: Backend):
    resource_state_name = "demo_state"
    component_name = "demo_component"
    no_cloud_output_resource = sample_data.simple_create_resource_changes(component_name)[0]
    cloud_output_resource =  sample_data.simple_create_resource_change_with_output(component_name)[1]

    changes = [(no_cloud_output_resource, {}), cloud_output_resource]

    resource_state_uuid = _create_simple_resource_state_and_component(test_backend,  resource_state_name, component_name)
    # Create a resource change then automatically complete the transaction
    for resource_change, cloud_output in changes:
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
            cloud_output
        )


    with pytest.raises(CloudOutputDoesNotExist):
        test_backend.get_cloud_output_value_by_name(
            resource_state_uuid, 
            component_name, 
            changes[0][0].new_resource.ruuid, 
            changes[0][0].new_resource.name, 
            "any"
        )


    with pytest.raises(KeyNotInCloudOutput):
        test_backend.get_cloud_output_value_by_name(
            resource_state_uuid, 
            component_name, 
            changes[1][0].new_resource.ruuid, 
            changes[1][0].new_resource.name, 
            "incorrect_key"
        )
    
    
    with pytest.raises(CloudOutputDoesNotExist):
        test_backend.get_cloud_output_value_by_hash(
            resource_state_uuid, 
            component_name, 
            changes[0][0].new_resource.ruuid, 
            changes[0][0].new_resource.hash, 
            "any"
        )


    with pytest.raises(KeyNotInCloudOutput):
        test_backend.get_cloud_output_value_by_hash(
            resource_state_uuid, 
            component_name, 
            changes[1][0].new_resource.ruuid, 
            changes[1][0].new_resource.hash, 
            "incorrect_key"
        )


################################
#### Simple Difference Tests
################################

def simple_differences(test_backend: Backend):
    new_components, previous_components = sample_data.simple_component_differences()

    resource_state_uuid = test_backend.create_resource_state("demo")

    
    [test_backend.create_component(resource_state_uuid, x.name) for x in previous_components]


    # Create the previous resource states:
    for component in previous_components:
        for resource in component.resources:
            resource_change = Resource_Difference(
                Resource_Change_Type.CREATE,
                component.name,
                None,
                resource
            )


            tmp_transaction = test_backend.create_resource_change(
                                resource_state_uuid, 
                                component.name, 
                                resource_change
                            )

            # no cloud output
            test_backend.complete_resource_change(
                resource_state_uuid,
                component.name,
                resource_change, 
                tmp_transaction, 
                {}
            )

    
    component_diffs, _, resource_diffs = test_backend.create_differences(resource_state_uuid, new_components, [x.name for x in previous_components])

    
    assert len(resource_diffs) == 4


    for x in component_diffs:
        print(x)


    assert False
    




    

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
