from networkx.algorithms import components
from rich.console import Console
from typing import Any, List, Tuple

from rich.progress import Progress, TaskID  

from core.constructs.components import Component_Change_Type, ComponentModel, Component_Difference
from core.constructs.resource import Resource_Change_Type, Resource_Difference, Resource_Reference_Change_Type, Resource_Reference_Difference

class OutputManager():



    def __init__(self, console: Console=None, progress: Progress=None) -> None:

        if console:
            self._console = console
        else:
            self._console = Console()

        if progress:
            self._progress = progress
        else:
            self._progress = None


    def print_header(self, resource_state_uuid: str):        
        print(f"Resource State: {resource_state_uuid}")

        print("")


    def print_local_state(self, rendered_components: List[ComponentModel]):

        rendered_components.sort(key=lambda x: x.name)
        
        self._console.print(f"Current State:")
        for component in rendered_components:
            self._console.print(f"Component: [bold blue]{component.name}[/bold blue]")

            if component.resources:
                self._console.print(f"    Resources:")
                for resource in component.resources:
                    self._console.print(f"        [bold blue]{resource.name} ({resource.ruuid})[/bold blue]")


            if component.references:
                self._console.print(f"    References:")
                for reference in component.references:
                    self._console.print(f"        [bold blue]From {reference.component_name} reference {reference.name} ({reference.ruuid})[/bold blue]")

        self._console.print("")


    def print_components_to_diff_against(self, old_component_names: List[str]):

        self._console.print("Components to diff against:")
        for component_name in old_component_names:
            self._console.print(f"    {component_name}")


        self._console.print("")


    def print_state_differences(self, differences: Tuple[List[Component_Difference], List[Resource_Difference], List[Resource_Reference_Difference]]):
        component_differences = differences[0]
        resource_differences = differences[1]
        reference_differences = differences[2]


        self._console.print(f"[bold white]Differences in State:[/bold white]")

        for component_diff in component_differences:
            if component_diff.action_type == Component_Change_Type.UPDATE_NAME:
                self._console.print(f"    [bold yellow]Update Name: [/bold yellow][bold blue]{component_diff.previous_name} to {component_diff.new_name} (component)[/bold blue]")
                continue

            elif component_diff.action_type == Component_Change_Type.UPDATE_IDENTITY:
                self._console.print(f"    [bold yellow]Update Identity: [/bold yellow][bold blue]{component_diff.new_name} (component)[/bold blue]")

            elif component_diff.action_type == Component_Change_Type.CREATE:
                self._console.print(f"    [bold green]Create: [/bold green][bold blue]{component_diff.new_name} (component)[/bold blue]")

            elif component_diff.action_type == Component_Change_Type.DELETE:
                self._console.print(f"    [bold red]Delete: [/bold red] [bold blue]{component_diff.new_name} (component)[/bold blue]")


            resource_changes = [x for x in resource_differences if x.component_name == component_diff.new_name]

            if resource_changes:
                for resource_diff in resource_changes:
                    if resource_diff.action_type == Resource_Change_Type.CREATE:
                        self._console.print(f"        [bold green]Create:[/bold green][bold blue] {resource_diff.new_resource.name} ({resource_diff.new_resource.ruuid})[/bold blue]")

                    elif resource_diff.action_type == Resource_Change_Type.DELETE:
                        self._console.print(f"        [bold red]Delete:[/bold red][bold blue] {resource_diff.previous_resource.name} ({resource_diff.previous_resource.ruuid})[/bold blue]")

                    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
                        self._console.print(f"        [bold yellow]Update:[/bold yellow][bold blue] {resource_diff.new_resource.name} ({resource_diff.new_resource.ruuid})[/bold blue]")

                    elif resource_diff.action_type == Resource_Change_Type.UPDATE_NAME:
                        self._console.print(f"        [bold yellow]Update Name:[/bold yellow][bold blue] from {resource_diff.previous_resource.name} to {resource_diff.new_resource.name} ({resource_diff.new_resource.ruuid})[/bold blue]")


            reference_changes = [x for x in reference_differences if x.originating_component_name == component_diff.new_name]

            if reference_changes:
                for reference_diff in reference_changes:
                    if reference_diff.action_type == Resource_Reference_Change_Type.CREATE:
                        self._console.print(f"        [bold green]Create reference:[/bold green][bold blue] {reference_diff.resource_reference.name} ({reference_diff.resource_reference.ruuid}) from {reference_diff.originating_component_name}[/bold blue]")

                    elif reference_diff.action_type == Resource_Reference_Change_Type.DELETE:
                        self._console.print(f"        [bold red]Delete reference:[/bold red][bold blue] {reference_diff.resource_reference.name} ({reference_diff.resource_reference.ruuid}) from {reference_diff.originating_component_name}[/bold blue]")


    def create_task(self, description: str, start: bool = True, total: int = 100, completed: int = 0, visible: bool = True, **fields: Any) -> 'OutputTask':
        """Create a task for the progress object in this output manager. 

        Raises:
            Exception: [description]

        Returns:
            OutputTask: Object to use to track the progress of the event
        """


        if not self._progress:
            raise Exception


        task_id = self._progress.add_task(description=description, start=start, total=total, completed=completed, visible=visible, **fields)

        return OutputTask(self, task_id)


class OutputTask():
    """
    Wrapper around a Progress Task from rich that is tied to a specific Output Manager
    """  

    def __init__(self, output_manager: OutputManager, task_id: TaskID) -> None:
        self._output_manager = output_manager
        self._task_id = task_id


    def update(self, *args, total: float = None, completed: float = None, advance: None = None, description: str = None, visible: bool = None, refresh: bool = False, **fields: Any):
        self._output_manager._progress.update(self._task_id, *args, total=total, completed=completed, advance=advance, description=description, visible=visible, refresh=refresh, **fields)


    def start_task(self):
        self._output_manager._progress.start_task(self._task_id)
