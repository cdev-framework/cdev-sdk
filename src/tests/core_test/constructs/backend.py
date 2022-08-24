from core.constructs.resource import (
    Resource_Change_Type,
    Resource_Difference,
    Resource_Reference_Change_Type,
    Resource_Reference_Difference,
    TaggableResourceModel,
)
from core.constructs.components import (
    Component_Change_Type,
    Component_Difference,
)
import pytest
from typing import Dict, List, Tuple

from core.constructs.backend import Backend
from core.constructs.backend_exceptions import *

from .. import sample_data

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
    sample_delete_resource_changes = sample_data.simple_delete_resource_changes(
        component_name
    )

    resource_state_uuid = _create_simple_resource_state_and_component(
        test_backend, resource_state_name, component_name
    )
    # Create a resource change then automatically complete the transaction
    for resource_change in final_state:
        (
            tmp_transaction,
            tmp_namespace,
        ) = test_backend.create_resource_change_transaction(
            resource_state_uuid, component_name, resource_change
        )

        # no cloud output
        test_backend.complete_resource_change(
            resource_state_uuid, component_name, resource_change, tmp_transaction, {}
        )

    returned_component = test_backend.get_component(resource_state_uuid, component_name)

    assert len(final_state) == len(returned_component.resources)

    # Try deleting a component that still has resources
    with pytest.raises(ComponentNotEmpty):
        _delete_component(test_backend, resource_state_uuid, component_name)

    # Delete resources
    for resource_change in sample_delete_resource_changes:
        (
            tmp_transaction,
            tmp_namespace,
        ) = test_backend.create_resource_change_transaction(
            resource_state_uuid, component_name, resource_change
        )

        test_backend.complete_resource_change(
            resource_state_uuid, component_name, resource_change, tmp_transaction, {}
        )

    returned_component = test_backend.get_component(resource_state_uuid, component_name)

    assert 0 == len(returned_component.resources)

    with pytest.raises(Exception):
        test_backend.delete_resource_state(resource_state_uuid)

    _delete_component(test_backend, resource_state_uuid, component_name)

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

    resource_state_uuid = _create_simple_resource_state_and_component(
        test_backend, resource_state_name, component_name
    )

    # Create a resource change then automatically complete the transaction
    for resource_change, cloud_output in final_state:
        (
            tmp_transaction,
            tmp_namespace,
        ) = test_backend.create_resource_change_transaction(
            resource_state_uuid, component_name, resource_change
        )

        test_backend.complete_resource_change(
            resource_state_uuid,
            component_name,
            resource_change,
            tmp_transaction,
            cloud_output,
        )

    desired_final_state = [
        (resource_change.new_resource, original_output, "arn")
        for resource_change, original_output in final_state
    ]

    _check_final_resources_and_output(
        test_backend, resource_state_uuid, component_name, desired_final_state
    )


def simple_references(test_backend: Backend):
    """
    Create a single component and add some resources. Then delete the resources and
    component.
    """
    resource_state_name = "demo_state"
    component1_name = "demo_component"
    component2_name = "demo_component2"

    resource_state_uuid = _create_simple_resource_state_and_component(
        test_backend, resource_state_name, component1_name
    )

    _create_component(test_backend, resource_state_uuid, component2_name)

    sample_create_resources = sample_data.simple_create_resource_changes(
        component1_name
    )
    sample_create_references = sample_data.simple_create_references(
        component1_name, component2_name
    )
    sample_delete_references = sample_data.simple_delete_references(
        component1_name, component2_name
    )

    for resource_change in sample_create_resources:
        (
            tmp_transaction,
            tmp_namespace,
        ) = test_backend.create_resource_change_transaction(
            resource_state_uuid, component1_name, resource_change
        )

        # no cloud output
        test_backend.complete_resource_change(
            resource_state_uuid, component1_name, resource_change, tmp_transaction, {}
        )

    for reference_change in sample_create_references:
        test_backend.resolve_reference_change(resource_state_uuid, reference_change)

    comp2 = test_backend.get_component(resource_state_uuid, component2_name)

    assert len(sample_create_references) == len(comp2.references)

    for reference_change in sample_delete_references:
        test_backend.resolve_reference_change(resource_state_uuid, reference_change)

    comp2 = test_backend.get_component(resource_state_uuid, component2_name)

    assert 0 == len(comp2.references)


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

    _create_simple_resource_state_and_component(
        test_backend, resource_state_name, component_name
    )

    with pytest.raises(ResourceStateAlreadyExists):
        _create_simple_resource_state_and_component(
            test_backend, resource_state_name, component_name
        )


def conflicting_names_component(test_backend: Backend):
    """
    Create a single component and add some resources. Then delete the resources and
    component.
    """
    resource_state_name = "demo_state"
    component_name = "demo_component"

    resource_state_uuid = _create_simple_resource_state_and_component(
        test_backend, resource_state_name, component_name
    )

    with pytest.raises(ComponentAlreadyExists):
        _create_component(test_backend, resource_state_uuid, component_name)


def get_missing_component(test_backend: Backend):
    resource_state_name = "demo_state"
    component_name = "demo_component"

    resource_state_uuid = _create_simple_resource_state_and_component(
        test_backend, resource_state_name, component_name
    )

    _delete_component(test_backend, resource_state_uuid, component_name)

    with pytest.raises(ComponentDoesNotExist):
        test_backend.get_component(resource_state_uuid, component_name)


def get_missing_resource(test_backend: Backend):
    resource_state_name = "demo_state"
    component_name = "demo_component"

    resource_state_uuid = _create_simple_resource_state_and_component(
        test_backend, resource_state_name, component_name
    )
    # Create a resource change then automatically complete the transaction

    with pytest.raises(ResourceDoesNotExist):
        test_backend.get_resource_by_name(
            resource_state_uuid, component_name, "cdev::resource", "demo_name"
        )

    with pytest.raises(ResourceDoesNotExist):
        test_backend.get_resource_by_hash(
            resource_state_uuid, component_name, "cdev::resource", "1 "
        )


def get_missing_cloud_output(test_backend: Backend):
    resource_state_name = "demo_state"
    component_name = "demo_component"
    no_cloud_output_resource = sample_data.simple_create_resource_changes(
        component_name
    )[0]
    cloud_output_resource = sample_data.simple_create_resource_change_with_output(
        component_name
    )[1]

    changes = [(no_cloud_output_resource, {}), cloud_output_resource]

    resource_state_uuid = _create_simple_resource_state_and_component(
        test_backend, resource_state_name, component_name
    )
    # Create a resource change then automatically complete the transaction
    for resource_change, cloud_output in changes:
        (
            tmp_transaction,
            tmp_namespace,
        ) = test_backend.create_resource_change_transaction(
            resource_state_uuid, component_name, resource_change
        )

        # no cloud output
        test_backend.complete_resource_change(
            resource_state_uuid,
            component_name,
            resource_change,
            tmp_transaction,
            cloud_output,
        )

    with pytest.raises(CloudOutputDoesNotExist):
        test_backend.get_cloud_output_value_by_name(
            resource_state_uuid,
            component_name,
            changes[0][0].new_resource.ruuid,
            changes[0][0].new_resource.name,
            "any",
        )

    with pytest.raises(KeyNotInCloudOutput):
        test_backend.get_cloud_output_value_by_name(
            resource_state_uuid,
            component_name,
            changes[1][0].new_resource.ruuid,
            changes[1][0].new_resource.name,
            "incorrect_key",
        )

    with pytest.raises(CloudOutputDoesNotExist):
        test_backend.get_cloud_output_value_by_hash(
            resource_state_uuid,
            component_name,
            changes[0][0].new_resource.ruuid,
            changes[0][0].new_resource.hash,
            "any",
        )

    with pytest.raises(KeyNotInCloudOutput):
        test_backend.get_cloud_output_value_by_hash(
            resource_state_uuid,
            component_name,
            changes[1][0].new_resource.ruuid,
            changes[1][0].new_resource.hash,
            "incorrect_key",
        )


################################
#### Simple Difference Tests
################################


def simple_differences(test_backend: Backend):
    new_components, previous_components = sample_data.simple_component_differences()

    resource_state_uuid = test_backend.create_resource_state("demo")

    [
        _create_component(test_backend, resource_state_uuid, x.name)
        for x in previous_components
    ]

    # Create the previous resource states:
    for component in previous_components:
        for resource in component.resources:
            resource_change = Resource_Difference(
                Resource_Change_Type.CREATE, component.name, None, resource
            )

            (
                tmp_transaction,
                tmp_namespace,
            ) = test_backend.create_resource_change_transaction(
                resource_state_uuid, component.name, resource_change
            )

            # no cloud output
            test_backend.complete_resource_change(
                resource_state_uuid,
                component.name,
                resource_change,
                tmp_transaction,
                {},
            )

        for reference in component.references:
            reference_change = Resource_Reference_Difference(
                Resource_Reference_Change_Type.CREATE, component.name, reference
            )

            test_backend.resolve_reference_change(resource_state_uuid, reference_change)

    new_components.insert(
        0, test_backend.get_component(resource_state_uuid, previous_components[0].name)
    )

    rename_component = test_backend.get_component(
        resource_state_uuid, previous_components[-1].name
    )

    rename_component.name = f"{rename_component.name}{rename_component.name}"

    new_components.append(rename_component)

    component_diffs, resource_diffs, reference_diffs = test_backend.create_differences(
        resource_state_uuid, new_components, [x.name for x in previous_components]
    )

    # TODO do more in depth testing of the actual diffs
    assert 4 == len(resource_diffs)
    assert 4 == len(component_diffs)
    assert 2 == len(reference_diffs)


def _create_simple_resource_state_and_component(
    test_backend: Backend, resource_state_name: str, component_name: str
):
    """
    Create resource state with a single empty component
    """
    # All create resources
    resource_state_uuid = test_backend.create_resource_state(resource_state_name, None)

    # Test that the resource state was added as a top level resource state
    assert (
        resource_state_uuid == test_backend.get_resource_state(resource_state_uuid).uuid
    )

    _create_component(test_backend, resource_state_uuid, component_name)

    returned_component = test_backend.get_component(resource_state_uuid, component_name)

    # Test we can get the component correctly
    assert component_name == returned_component.name

    return resource_state_uuid


def _check_final_resources_and_output(
    test_backend: Backend,
    resource_state_uuid: str,
    component_name: str,
    final_state: List[Tuple[TaggableResourceModel, Dict, str]],
):
    # Assert:
    #   All resources names are there
    #   All resources can be accessed by name
    #   All resources can be accessed by hash
    #   All cloud outputs can be access by name
    #   All cloud outputs can be access by hash

    returned_component = test_backend.get_component(resource_state_uuid, component_name)

    resource_names = set(x.name for x in returned_component.resources)

    assert all((resource.name in resource_names) for resource, _, _ in final_state)
    assert all(
        (
            resource
            == test_backend.get_resource_by_name(
                resource_state_uuid, component_name, resource.ruuid, resource.name
            )
        )
        for resource, _, _ in final_state
    )
    assert all(
        (
            resource
            == test_backend.get_resource_by_hash(
                resource_state_uuid, component_name, resource.ruuid, resource.hash
            )
        )
        for resource, _, _ in final_state
    )
    assert all(
        (
            original_output.get(key)
            == test_backend.get_cloud_output_value_by_name(
                resource_state_uuid, component_name, resource.ruuid, resource.name, key
            )
        )
        for resource, original_output, key in final_state
    )
    assert all(
        (
            original_output.get(key)
            == test_backend.get_cloud_output_value_by_hash(
                resource_state_uuid, component_name, resource.ruuid, resource.hash, key
            )
        )
        for resource, original_output, key in final_state
    )


def _create_component(backend: Backend, resource_state_uuid: str, component_name: str):

    create_comp_diff = Component_Difference(
        action_type=Component_Change_Type.CREATE, new_name=component_name
    )

    backend.update_component(resource_state_uuid, create_comp_diff)


def _delete_component(backend: Backend, resource_state_uuid: str, component_name: str):

    create_comp_diff = Component_Difference(
        action_type=Component_Change_Type.DELETE, previous_name=component_name
    )

    backend.update_component(resource_state_uuid, create_comp_diff)
