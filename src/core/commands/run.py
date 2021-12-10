from ..constructs.commands import BaseCommand, BaseCommandContainer

from ..constructs.workspace import Workspace



WORKSPACE = Workspace.instance()


def run_command(args):
    """
    Attempts to find and run a user defined command 

    format:
    cdev run <sub_command> <args> 
    """
    print(f"CALLING RUN COMMAND")
    # Convert namespace into dict
    params = vars(args)

    # This is the command to run... It can be a single command or a path to the command where the path is '.' delimitated
    sub_command = params.get("subcommand")
    cli_args = params.get("args") if params.get("args") else []
    
    try:
        WORKSPACE.execute_command(sub_command, cli_args)
    except Exception as e:
        print(e)
        return
        

    
    



