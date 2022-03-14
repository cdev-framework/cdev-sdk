
from ..constructs.workspace import Workspace
from ..constructs.output_manager import OutputManager

from core.utils.logger import log

def cloud_output_command_cli(args):
    config = args[0]
    cloud_output_command(config)


def cloud_output_command(workspace: Workspace, output: OutputManager, cloud_output_id: str, only_value: bool):
    log.debug("Executing Frontend")

   

    split_names = cloud_output_id.split('.')

    if not len(split_names) == 4:
        raise Exception("Output not provided in correct structure. ex: <component>.<ruuid>.<cdev_name>.<output_key>")


    component_name = split_names[0]
    resource_ruuid = f"cdev::simple::{split_names[1]}"
    resource_name = split_names[2]
    output_key = split_names[3]


    try:
        cloud_output = workspace.get_backend().get_cloud_output_by_name(
            workspace.get_resource_state_uuid(),
            component_name,
            resource_ruuid,
            resource_name
        )
    except Exception as e:
        print(e)
        raise e


    if not output_key in cloud_output:
        raise Exception(f"Key {output_key} not in Cloud Output {cloud_output}")


    if not only_value:
        print(f"{output_key} -> {cloud_output.get(output_key)}")
    else:
        print(cloud_output.get(output_key))