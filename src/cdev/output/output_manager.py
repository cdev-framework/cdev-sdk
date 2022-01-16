from rich import print

from core.output.output_manager import OutputManager

from ..constructs.project import Project



class CdevOutputManager(OutputManager):


    def print_header(self):
        myproject = Project.instance()

        print("")
        print(f"Project: {myproject.get_name()}")
