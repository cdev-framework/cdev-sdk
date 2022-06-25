from cdev.constructs.project import Project
from rich.prompt import Confirm

from core.constructs.output_manager import OutputManager
from core.constructs.workspace import Workspace_State


def destroy_command_cli(
    project: Project, output_manager: OutputManager, **kwargs
) -> None:
    destroy_command(project, output_manager)


def destroy_command(project: Project, output_manager: OutputManager) -> None:

    ws = project.get_current_environment().get_workspace()

    ws.set_state(Workspace_State.EXECUTING_FRONTEND)

    diff_previous_component_names = [
        x.name
        for x in ws.get_backend()
        .get_resource_state(ws.get_resource_state_uuid())
        .components
    ]

    differences = ws.create_state_differences([], diff_previous_component_names)

    if any(x for x in differences):
        output_manager.print_state_differences(differences)

    print("")
    do_deployment = Confirm.ask("Are you sure you want to Destroy the environment?")

    if not do_deployment:
        return

    differences_structured = ws.sort_differences(differences)
    ws.set_state(Workspace_State.EXECUTING_BACKEND)

    ws.deploy_differences(differences_structured)
