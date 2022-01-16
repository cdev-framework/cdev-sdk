from rich import print
from typing import List

from core.constructs.components import ComponentModel
from core.constructs.workspace import Workspace

class OutputManager():


    def print_header(self):
        ws = Workspace.instance()

        resource_state_uuid = ws.get_resource_state_uuid()
        print(f"Resource State: {resource_state_uuid}")


    def print_local_state(self, rendered_components: List[ComponentModel]):
        self.print_header()

        rendered_components.sort(key=lambda x: x.name)
        
        print("")
        print(f"Current State:")
        for component in rendered_components:
            print(f"Component: {component.name}")

            if component.resources:
                print(f"    Resources:")
                for resource in component.resources:

                    print(f"        [bold blue]{resource.name} ({resource.ruuid})[/bold blue]")


            if component.references:
                print(f"    References:")
                for reference in component.references:
                    print(f"        [bold blue]From {reference.component_name} reference {reference.name} ({reference.ruuid})[/bold blue]")
