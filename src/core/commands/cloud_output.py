from dataclasses import dataclass, field
from typing import List

from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager

from core.utils.exceptions import cdev_core_error


@dataclass
class InputError(cdev_core_error):
    help_message: str = "   The cloud output identifier should be of the form <component>.<ruuid>.<cdev_name>.<output_key>"
    help_resources: List[str] = field(default_factory=lambda: [])


def cloud_output_command_cli(args) -> None:
    config = args[0]
    cloud_output_command(config)


def cloud_output_command(
    workspace: Workspace,
    output: OutputManager,
    cloud_output_id: str,
    only_value: bool = False,
) -> None:
    """Command to get the Cloud Output values from a given id.

    Args:
        workspace (Workspace): The Workspace that the command is executed within.
        output (OutputManager): object to pass all output to.
        cloud_output_id (str): Id of the output to get <component>.<ruuid>.<cdev_name>.<output_key>
        only_value (bool): Output only the value. Helpful for shell scripting.

    Raises:
        Exception
    """
    split_names = cloud_output_id.split(".")

    if len(split_names) != 4:
        raise InputError(
            f"Cloud Output Identifier '{cloud_output_id}' is not provided in correct structure"
        )

    component_name = split_names[0]
    resource_ruuid = f"cdev::simple::{split_names[1]}"
    resource_name = split_names[2]
    output_key = split_names[3]

    cloud_output = workspace.get_backend().get_cloud_output_value_by_name(
        workspace.get_resource_state_uuid(),
        component_name,
        resource_ruuid,
        resource_name,
        output_key,
    )

    # LEAVE AS REGULAR PRINTS BECAUSE OF EMOJI ISSUE
    if not only_value:
        print(f"{output_key} -> {cloud_output}")
    else:
        print(cloud_output)
