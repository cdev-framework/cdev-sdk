from core.constructs.workspace import Workspace
from core.constructs.output_manager import OutputManager

from core.utils.logger import log


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
    log.debug("Executing Frontend")

    split_names = cloud_output_id.split(".")

    if len(split_names) != 4:
        raise Exception(
            "Output not provided in correct structure. ex: <component>.<ruuid>.<cdev_name>.<output_key>"
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

    if not only_value:
        print(f"{output_key} -> {cloud_output.get(output_key)}")
    else:
        print(cloud_output.get(output_key))
