"""Utilities for displaying data in a unified and formatted manner



"""

from rich.console import Console
from typing import Any, List, Tuple, Union

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
                self._console.print(f"    [bold red]Delete: [/bold red] [bold blue]{component_diff.previous_name} (component)[/bold blue]")


            resource_changes = [x for x in resource_differences if x.component_name == component_diff.new_name or x.component_name == component_diff.previous_name ]

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


    def create_output_description(self, node: Union[Resource_Difference, Resource_Reference_Difference, Component_Difference]) -> str:
        if isinstance(node, Resource_Difference):
            if node.action_type == Resource_Change_Type.CREATE:
                return f"[bold green]Creating:[/bold green][bold blue] {node.new_resource.name} ({node.new_resource.ruuid})[/bold blue]"

            elif node.action_type == Resource_Change_Type.DELETE:
                return f"[bold red]Deleting:[/bold red][bold blue] {node.previous_resource.name} ({node.previous_resource.ruuid})[/bold blue]"

            elif node.action_type == Resource_Change_Type.UPDATE_IDENTITY:
                return f"[bold yellow]Updating:[/bold yellow][bold blue] {node.new_resource.name} ({node.new_resource.ruuid})[/bold blue]"

            elif node.action_type == Resource_Change_Type.UPDATE_NAME:
                return f"[bold yellow]Updating Name:[/bold yellow][bold blue] from {node.previous_resource.name} to {node.new_resource.name} ({node.new_resource.ruuid})[/bold blue]"

        elif isinstance(node, Resource_Reference_Difference):
            if node.action_type == Resource_Reference_Change_Type.CREATE:
                return f"[bold green]Create reference:[/bold green][bold blue] {node.resource_reference.name} ({node.resource_reference.ruuid}) from {node.originating_component_name}[/bold blue]"

            elif node.action_type == Resource_Reference_Change_Type.DELETE:
                return f"[bold red]Delete reference:[/bold red][bold blue] {node.resource_reference.name} ({node.resource_reference.ruuid}) from {node.originating_component_name}[/bold blue]"

        elif isinstance(node, Component_Difference):
            if node.action_type == Component_Change_Type.UPDATE_NAME:
                return f"[bold yellow]Update Name: [/bold yellow][bold blue]{node.previous_name} to {node.new_name} (component)[/bold blue]"

            elif node.action_type == Component_Change_Type.UPDATE_IDENTITY:
                return f"[bold yellow]Update Identity: [/bold yellow][bold blue]{node.new_name} (component)[/bold blue]"

            elif node.action_type == Component_Change_Type.CREATE:
                return f"[bold green]Create: [/bold green][bold blue]{node.new_name} (component)[/bold blue]"

            elif node.action_type == Component_Change_Type.DELETE:
                return f"[bold red]Delete: [/bold red] [bold blue]{node.previous_name} (component)[/bold blue]"

        else:
            raise Exception(f"Trying to deploy node {node} but it is not a correct type ")


class OutputTask():
    """
    Wrapper around an output that can be used to track long running events. The implementation is as a wrapper around a 'progress task' from the
    rich library. Thus, the api for 'update' and 'start' follows the same pattern as that of a 'task' in the rich library. The print method provides
    access for sending messages to the parent console of this task. 
    """  

    def __init__(self, output_manager: OutputManager, task_id: TaskID) -> None:
        self._output_manager = output_manager
        self._task_id = task_id

    
    def print(self, msg: str):
        """Print a message to the parent output context.

        Args:
            msg (str): message to print
        """
        self._output_manager._console.print(msg)


    def print_error(self, msg: str):
        """
        Print a message as an error

        Args:
            msg (str): error message
        """
        self.print(f"[bold red]{msg}[/bold red]")



    def update(self, *args, total: float = None, completed: float = None, advance: None = None, description: str = None, visible: bool = None, refresh: bool = False, **fields: Any):
        #self._output_manager._console.print(fields.get('comment'))
        self._output_manager._progress.update(self._task_id, *args, total=total, completed=completed, advance=advance, description=description, visible=visible, refresh=refresh, **fields)


    def start_task(self):
        self._output_manager._progress.start_task(self._task_id)
