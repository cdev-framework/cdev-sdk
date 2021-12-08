from cdev.core.management.base import BaseCommand, BaseCommandContainer

from cdev.core.constructs.workspace import Workspace

from cdev.core.utils import  logger


log = logger.get_cdev_logger(__name__)


WORKSPACE = Workspace.instance()


def run_command(args):
    """
    Attempts to find and run a user defined command 

    format:
    cdev run <sub_command> <args> 
    """

    # Convert namespace into dict
    params = vars(args)

    # This is the command to run... It can be a single command or a path to the command where the path is '.' delimitated
    sub_command = params.get("subcommand")
    cli_args = params.get("args") if params.get("args") else []
    
    try:
        obj, program_name, command_name, is_command = WORKSPACE.find_command(sub_command)
    except Exception as e:
        print(e)
        return
        

    try:
        if is_command:
            if not isinstance(obj, BaseCommand):
                # Error message
                return

            args = [program_name, command_name, *cli_args]
            obj.run_from_command_line(args)
        else:
            if not isinstance(obj, BaseCommandContainer):
                # Error message
                return
            obj.display_help_message()
    except Exception as e:
        raise e
    




