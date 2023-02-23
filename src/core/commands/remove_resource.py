from dataclasses import dataclass, field
from typing import List

from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager

from core.utils.exceptions import cdev_core_error

from rich.prompt import Confirm


@dataclass
class InputError(cdev_core_error):
    help_message: str = "   The cloud output identifier should be of the form <component>.<ruuid>.<cdev_name>"
    help_resources: List[str] = field(default_factory=lambda: [])


def remove_resource_command_cli(args) -> None:
    config = args[0]
    remove_resource_command(config)


def remove_resource_command(
    workspace: Workspace,
    output: OutputManager,
    cloud_output_id: str,
    force: bool = False,
) -> None:
    """Command to get the Cloud Output values from a given id.

    Args:
        workspace (Workspace): The Workspace that the command is executed within.
        output (OutputManager): object to pass all output to.
        cloud_output_id (str): Id of the output to get <component>.<ruuid>.<cdev_name>
        force (bool): Output only the value. Helpful for shell scripting.

    Raises:
        Exception
    """
    split_names = cloud_output_id.split(".")

    if len(split_names) != 3:
        raise InputError(
            f"Cloud Output Identifier '{cloud_output_id}' is not provided in correct structure"
        )

    component_name = split_names[0]
    resource_ruuid = f"cdev::simple::{split_names[1]}"
    resource_name = split_names[2]

    try:
        workspace.get_backend().get_resource_by_name(
            workspace.get_resource_state_uuid(),
            component_name,
            resource_ruuid,
            resource_name,
        )
    except Exception as e:
        print("")
        output.print(
            f"[yellow]Can not remove {cloud_output_id}. It does not exist in the backend.[/yellow]"
        )
        return

    if not force:
        print("")
        output.print(
            "[bold]Note that removing a resource can have unintended side effects if the resource is referenced by other resources. "
            "This will only remove the resource from the backend, it will not delete any resource in the cloud. [/bold]"
        )
        print("")
        do_deployment = Confirm.ask(
            f"Are you sure you want to remove {cloud_output_id}?"
        )

        if not do_deployment:
            return

    previous_cloud_output = workspace.get_backend().get_cloud_output_by_name(
        workspace.get_resource_state_uuid(),
        component_name,
        resource_ruuid,
        resource_name,
    )

    workspace.get_backend().remove_resource(
        workspace.get_resource_state_uuid(),
        component_name,
        resource_ruuid,
        resource_name,
    )

    print("")
    output.print(f"[green]Successfully Removed {cloud_output_id} [/green]")
    print("")

    output.print(
        "These Cloud Outputs can be used to manually clean up resources in the Cloud:"
    )
    output.print(previous_cloud_output)
