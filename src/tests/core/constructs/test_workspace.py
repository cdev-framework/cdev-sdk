from typing import Dict
from core.constructs.backend import Backend
from core.constructs.cloud_output import cloud_output_model
from core.constructs.workspace import Workspace, Workspace_State, Workspace_Info
from core.constructs.resource import ResourceModel
from core.constructs.components import ComponentModel

from core.constructs.backend import Backend_Configuration
from core.constructs.settings import Settings_Info

from .. import sample_data


def simple_initialize_workspace(
    workspace: Workspace,
    settings_info: Settings_Info,
    backend_info: Backend_Configuration,
    resource_state_uuid: str,
    configuration: Dict,
):
    workspace.set_state(Workspace_State.INITIALIZING)
    workspace.initialize_workspace(
        settings_info=settings_info,
        backend_info=backend_info,
        resource_state_uuid=resource_state_uuid,
        configuration=configuration,
    )


def simple_execute_frontend_workspace(workspace: Workspace, config: Workspace_Info):
    components = sample_data.simple_components()

    workspace.set_state(Workspace_State.INITIALIZING)

    for component in components:
        workspace.add_component(component)

    workspace.initialize_workspace(config)
    workspace.set_state(Workspace_State.INITIALIZED)
    workspace.set_state(Workspace_State.EXECUTING_FRONTEND)

    state = workspace.generate_current_state()

    assert len(state) == len(components)


def simple_add_commands(workspace: Workspace, config: Workspace_Info):
    commands = sample_data.simple_commands()

    workspace.set_state(Workspace_State.INITIALIZING)

    for command in commands:
        workspace.add_command(command)

    workspace.initialize_workspace(config)

    workspace.set_state(Workspace_State.INITIALIZED)

    returned_commands = workspace.get_commands()

    assert len(commands) + 1 == len(returned_commands)


def _get_fake_backend():
    class FakeBackend(Backend):
        def __init__(self, **kwargs) -> None:
            pass

        def get_cloud_output_value_by_name(
            self,
            resource_state_uuid: str,
            component_name: str,
            resource_type: str,
            resource_name: str,
            key: str,
        ):
            id = ",".join(
                [resource_state_uuid, component_name, resource_type, resource_name, key]
            )

            data = {
                ",".join(["1", "comp1", "r", "r1", "cloud_id"]): "val1",
                ",".join(["1", "comp1", "r", "r2", "cloud_id"]): "val2",
                ",".join(["1", "comp1", "r", "r3", "cloud_id"]): "val3",
                ",".join(["1", "comp1", "r", "r4", "cloud_id"]): "val4",
                ",".join(["1", "comp1", "r", "r5", "cloud_id"]): "val5",
            }

            if not id in data:
                raise Exception

            return data.get(id)

        def get_component(
            self, resource_state_uuid: str, component_name: str
        ) -> ComponentModel:

            if not resource_state_uuid == "1":
                raise Exception

            if not component_name == "comp1":
                raise Exception

            return ComponentModel(
                name="comp1",
                hash="0",
                previous_resolved_cloud_values={
                    "r;e1": {
                        "r;r1;cloud_id": "val1",
                        "r;r2;cloud_id": "val2",
                        "r;r3;cloud_id": "val3",
                        "r;r4;cloud_id": "val4",
                        "r;r5;cloud_id": "val5",
                    }
                },
            )

    return FakeBackend()


def simple_evaluate_and_replace_cloud_output(workspace: Workspace):
    data = [
        (
            ResourceModel(
                **{
                    "name": "e1",
                    "ruuid": "r",
                    "hash": "0",
                    "val": cloud_output_model(
                        **{
                            "name": "r1",
                            "ruuid": "r",
                            "key": "cloud_id",
                            "type": "resource",
                            "id": "cdev_cloud_output",
                        }
                    ),
                }
            ),
            (
                ResourceModel(
                    **{"name": "e1", "ruuid": "r", "hash": "0", "val": "val1"}
                ),
                {"r;r1;cloud_id": "val1"},
            ),
        ),
        (
            ResourceModel(
                **{
                    "name": "e1",
                    "ruuid": "r",
                    "hash": "0",
                    "val": cloud_output_model(
                        **{
                            "name": "r2",
                            "ruuid": "r",
                            "key": "cloud_id",
                            "type": "resource",
                            "id": "cdev_cloud_output",
                        }
                    ),
                }
            ),
            (
                ResourceModel(
                    **{"name": "e1", "ruuid": "r", "hash": "0", "val": "val2"}
                ),
                {"r;r2;cloud_id": "val2"},
            ),
        ),
        (
            ResourceModel(
                **{
                    "name": "e1",
                    "ruuid": "r",
                    "hash": "0",
                    "val": cloud_output_model(
                        **{
                            "name": "r3",
                            "ruuid": "r",
                            "key": "cloud_id",
                            "type": "resource",
                            "id": "cdev_cloud_output",
                        }
                    ),
                }
            ),
            (
                ResourceModel(
                    **{"name": "e1", "ruuid": "r", "hash": "0", "val": "val3"}
                ),
                {"r;r3;cloud_id": "val3"},
            ),
        ),
    ]

    for input, expected_result in data:
        rv = workspace.evaluate_and_replace_cloud_output("comp1", input)
        assert rv == expected_result


def simple_evaluate_and_replace_previous_cloud_output(workspace: Workspace):
    data = [
        (
            ResourceModel(
                **{
                    "name": "e1",
                    "ruuid": "r",
                    "hash": "0",
                    "val": cloud_output_model(
                        **{
                            "name": "r1",
                            "ruuid": "r",
                            "key": "cloud_id",
                            "type": "resource",
                            "id": "cdev_cloud_output",
                        }
                    ),
                }
            ),
            ResourceModel(**{"name": "e1", "ruuid": "r", "hash": "0", "val": "val1"}),
        ),
        (
            ResourceModel(
                **{
                    "name": "e1",
                    "ruuid": "r",
                    "hash": "0",
                    "val": cloud_output_model(
                        **{
                            "name": "r2",
                            "ruuid": "r",
                            "key": "cloud_id",
                            "type": "resource",
                            "id": "cdev_cloud_output",
                        }
                    ),
                }
            ),
            ResourceModel(**{"name": "e1", "ruuid": "r", "hash": "0", "val": "val2"}),
        ),
        (
            ResourceModel(
                **{
                    "name": "e1",
                    "ruuid": "r",
                    "hash": "0",
                    "val": cloud_output_model(
                        **{
                            "name": "r3",
                            "ruuid": "r",
                            "key": "cloud_id",
                            "type": "resource",
                            "id": "cdev_cloud_output",
                        }
                    ),
                }
            ),
            ResourceModel(**{"name": "e1", "ruuid": "r", "hash": "0", "val": "val3"}),
        ),
    ]

    for input, expected_result in data:
        rv = workspace.evaluate_and_replace_previous_cloud_output("comp1", input)
        print(rv)
        assert rv == expected_result


#######################
##### Base Class Tests
#######################

# The base class implements some of the generic functionality so test that here


def test_evaluate_and_replace_cloud_output():

    ws = Workspace()

    ws.get_backend = _get_fake_backend
    ws.get_state = lambda: Workspace_State.EXECUTING_BACKEND
    ws.get_resource_state_uuid = lambda: "1"

    simple_evaluate_and_replace_cloud_output(ws)


def test_evaluate_and_replace_previous_cloud_output():

    ws = Workspace()

    ws.get_backend = _get_fake_backend
    ws.get_state = lambda: Workspace_State.EXECUTING_BACKEND
    ws.get_resource_state_uuid = lambda: "1"

    simple_evaluate_and_replace_previous_cloud_output(ws)
