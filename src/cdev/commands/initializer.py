
import os
from ..utils import project

from rich.prompt import Prompt

def init(args):
    base_project_dir = os.getcwd()

    if project.check_if_project_exists():
        print(f"A project is already initialized at {base_project_dir}")
        return

    project_name = Prompt.ask("Enter your project name")

    info = project.project_definition(base_project_dir, project_name, ['prod', 'stage', 'dev'])

    project.create_new_project(info)

    return
