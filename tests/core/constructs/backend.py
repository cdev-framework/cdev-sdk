from core.constructs.backend import Backend



def sample(test_backend: Backend):
    resource_state_uuid = test_backend.create_resource_state("1", None)
    component_uuid = test_backend.create_component(resource_state_uuid, "2")

    returned_component = test_backend.get_component(resource_state_uuid, "2")

    assert "2" == returned_component.name
