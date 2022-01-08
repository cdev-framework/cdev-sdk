from ..constructs.workspace import Workspace


def create_resource_state_cli(args):

    WORKSPACE = Workspace.instance()

    create_resource_state(WORKSPACE)


def create_resource_state(workspace: Workspace):
    new_uuid = workspace.get_backend().create_resource_state("demo")
    print(new_uuid)
