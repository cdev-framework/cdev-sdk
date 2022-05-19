from rich import print
from typing import List

from core.constructs.output_manager import OutputManager

from ..constructs.project import Project


class CdevOutputManager(OutputManager):

    def print_header(self) -> None:
        my_project = Project.instance()

        print("")
        print(f"Project: {my_project.get_name()}")
        print("")

    def print_components_to_diff_against(self, old_component_names: List[str]) -> None:
        pass
