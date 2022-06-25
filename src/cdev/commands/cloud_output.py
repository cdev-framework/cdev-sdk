from cdev.constructs.project import Project
from cdev.default.output_manager import CdevOutputManager
from cdev.cli.logger import set_global_logger_from_cli


from core.commands.cloud_output import cloud_output_command as core_cloud_output_command


def cloud_output_command_cli(args) -> None:
    config = args[0]
    set_global_logger_from_cli(config.loglevel)
    cloud_output_command(config.cloud_output_id, config.value)


def cloud_output_command(cloud_output_id: str, only_value: bool) -> None:

    output_manager = CdevOutputManager()
    my_project = Project.instance()

    ws = my_project.get_current_environment_workspace()

    core_cloud_output_command(ws, output_manager, cloud_output_id, only_value)
