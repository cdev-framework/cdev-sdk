from cdev.constructs.project import Project
from cdev.default.output_manager import CdevOutputManager
from cdev.cli.logger import set_global_logger_from_cli
from rich.prompt import Confirm


from core.constructs.workspace import Workspace_State


def destroy_command_cli(args) -> None:
    config = args[0]
    set_global_logger_from_cli(config.loglevel)
    destroy_command(args)


def destroy_command(args) -> None:

    my_project = Project.instance()
    ws = my_project.get_current_environment().get_workspace()
    ws.set_state(Workspace_State.EXECUTING_FRONTEND)

    diff_previous_component_names = [
        x.name
        for x in ws.get_backend()
        .get_resource_state(ws.get_resource_state_uuid())
        .components
    ]

    differences = ws.create_state_differences([], diff_previous_component_names)

    if any(differences):
        output_manager = CdevOutputManager()
        output_manager.print_state_differences(differences)

    print("")
    do_deployment = Confirm.ask("Are you sure you want to Destroy the environment?")
    if do_deployment is not True:
        return

    differences_structured = ws.sort_differences(differences)
    ws.set_state(Workspace_State.EXECUTING_BACKEND)
    ws.deploy_differences(differences_structured)
