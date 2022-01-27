from typing import Dict
from core.constructs.backend import Backend
from core.constructs.output import cloud_output_model
from core.constructs.workspace import Workspace, Workspace_State, Workspace_Info
from core.constructs.resource import ResourceModel

from .. import sample_data

def simple_initialize_workspace(workspace: Workspace, config: Dict):
    workspace.set_state(Workspace_State.INITIALIZING)
    workspace.initialize_workspace(config)
    


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

    assert len(commands)+1 == len(returned_commands)


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
            id = ",".join([resource_state_uuid, component_name, resource_type, resource_name, key])

            data = {
                ",".join(['1', 'comp1', "r", "r1", "cloud_id"]): "val1",
                ",".join(['1', 'comp1', "r", "r2", "cloud_id"]): "val2",
                ",".join(['1', 'comp1', "r", "r3", "cloud_id"]): "val3",
                ",".join(['1', 'comp1', "r", "r4", "cloud_id"]): "val4",
                ",".join(['1', 'comp1', "r", "r5", "cloud_id"]): "val5"
            }

            if not id in data:
                raise Exception

            return data.get(id)

    return FakeBackend()



def simple_evaluate_and_replace_cloud_output(workspace: Workspace):
    #workspace.set_state(Workspace_State.EXECUTING_BACKEND)

    workspace.get_backend = _get_fake_backend
    workspace.get_state = lambda: Workspace_State.EXECUTING_BACKEND
    workspace.get_resource_state_uuid = lambda: "1"

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
                            "id": "cdev_cloud_output"
                        }
                    )
                }
            ),
            ResourceModel(
                **{
                    "name": "e1",
                    "ruuid": "r",
                    "hash": "0",
                    "val": "val1"
                }
            )
        )
    ]

    for input, expected_result in data:
        rv = workspace.evaluate_and_replace_cloud_output("comp1", input)
        print(rv)
        print(expected_result)

        assert rv == expected_result


def test_evaluate_and_replace_cloud_output():
    ws = Workspace()

    simple_evaluate_and_replace_cloud_output(ws)
