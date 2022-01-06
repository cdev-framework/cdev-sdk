"""from typing_extensions import final
from core.backend import cloud_mapper_manager
from ..frontend import executer as frontend_executer
from .. import output as cdev_output
from ..utils import project, logger
from rich.markup import escape


from ..constructs import Cdev_Project


log = logger.get_cdev_logger(__name__)

def cloud_output_command(args):
    log.debug(f"Calling `cdev output`")
    project.initialize_project()
    log.debug(f"Initialized project")


    rendered_frontend = frontend_executer.execute_frontend()
    
    PROJECT = Cdev_Project()
    
    desired_outputs = PROJECT.get_outputs()

    rendered_outputs = []

    for label, output in desired_outputs.items(): 
        
        identifier = output.resource.split("::")[-1]

        if output.transformer:
            rendered_value = cloud_mapper_manager.get_output_value_by_hash(identifier, output.key, transformer=output.get("transformer"))
        else:
            rendered_value = cloud_mapper_manager.get_output_value_by_hash(identifier, output.key)

        final_val = escape(rendered_value)
        rendered_outputs.append(f"[magenta]{escape(label)}[/magenta] -> [green]{final_val}[/green]")

    cdev_output.print(f"---OUTPUTS---")
    for rendered_output in rendered_outputs:
        print(rendered_output)
"""
