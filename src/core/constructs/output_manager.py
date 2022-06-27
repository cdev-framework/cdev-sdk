"""Utilities for displaying data in a unified and formatted manner



"""

from rich.console import Console
from rich.traceback import Traceback
from typing import Any, List, Optional, Tuple, Union

from rich.progress import Progress, TaskID

from core.constructs.components import (
    Component_Change_Type,
    ComponentModel,
    Component_Difference,
)
from core.constructs.resource import (
    Resource_Change_Type,
    Resource_Difference,
    Resource_Reference_Change_Type,
    Resource_Reference_Difference,
)
from core.utils.exceptions import cdev_core_error, wrapped_base_exception


class CdevCoreConsole(Console):
    def print_exception(
        self,
        *,
        exception: BaseException,
        width: Optional[int] = 100,
        extra_lines: int = 3,
        theme: Optional[str] = None,
        word_wrap: bool = False,
        show_locals: bool = False,
    ) -> None:
        """Prints a rich render of the last exception and traceback.

        Args:
            width (Optional[int], optional): Number of characters used to render code. Defaults to 88.
            extra_lines (int, optional): Additional lines of code to render. Defaults to 3.
            theme (str, optional): Override pygments theme used in traceback
            word_wrap (bool, optional): Enable word wrapping of long lines. Defaults to False.
            show_locals (bool, optional): Enable display of local variables. Defaults to False.
        """

        _trace = Traceback.extract(
            type(exception), exception, exception.__traceback__, show_locals=show_locals
        )
        traceback = Traceback(
            trace=_trace,
            width=width,
            extra_lines=extra_lines,
            theme=theme,
            word_wrap=word_wrap,
            show_locals=show_locals,
        )
        self.print(traceback)


class OutputManager:
    def __init__(
        self, console: CdevCoreConsole = None, progress: Progress = None
    ) -> None:
        """Initialize the Output Manager

        Args:
            console (Console, optional): Defaults to None.
            progress (Progress, optional): Defaults to None.
        """
        self._console = console or CdevCoreConsole()
        self._progress = progress

    def print(self, msg: str) -> None:
        self._console.print(msg)

    def print_exception(self, exception: cdev_core_error):
        # self._console.print("TRACEBACK")
        if isinstance(exception, wrapped_base_exception):
            self._console.print_exception(exception=exception.original_exception)
        else:
            self._console.print_exception(exception=exception)
        self._console.print("")

        self._console.print(f"EXCEPTION: ")
        self._console.print(f"   {exception.error_message}")
        self._console.print("")

        self._console.print("GENERAL HELP MESSAGE:")
        self._console.print(exception.help_message)
        self._console.print("")

        self._console.print("RESOURCES THAT CAN HELP:")
        self._console.print(exception.help_resources)

    def print_header(self, resource_state_uuid: str) -> None:
        """Print the header of the output

        Args:
            resource_state_uuid (str)
        """
        print(f"Resource State: {resource_state_uuid}")
        print("")

    def print_local_state(self, rendered_components: List[ComponentModel]) -> None:
        """Print the current state

        Args:
            rendered_components (List[ComponentModel])
        """
        rendered_components.sort(key=lambda x: x.name)

        self._console.print(f"Current State:")
        for component in rendered_components:
            self._console.print(f"Component: [bold blue]{component.name}[/bold blue]")
            self._print_component_resources(component)
            self._print_component_references(component)

        self._console.print("")

    def print_components_to_diff_against(self, old_component_names: List[str]) -> None:
        """Print the component names we are diffing against

        Args:
            old_component_names (List[str])
        """

        self._console.print("Components to diff against:")
        for component_name in old_component_names:
            self._console.print(f"    {component_name}")

        self._console.print("")

    def print_state_differences(
        self,
        differences: Tuple[
            List[Component_Difference],
            List[Resource_Difference],
            List[Resource_Reference_Difference],
        ],
    ) -> None:
        """Print the differences in a state

        Args:
            differences (Tuple[ List[Component_Difference], List[Resource_Difference], List[Resource_Reference_Difference], ])
        """
        if not any(differences):
            return

        component_differences = differences[0]
        resource_differences = differences[1]
        reference_differences = differences[2]

        self._console.print(f"[bold white]Differences in State:[/bold white]")

        for component_diff in component_differences:
            self._print_component_differences(component_diff)
            self._print_component_resource_differences(
                component_diff, resource_differences
            )
            self._print_component_reference_differences(
                component_diff, reference_differences
            )

    def create_task(
        self,
        description: str,
        start: bool = True,
        total: int = 100,
        completed: int = 0,
        visible: bool = True,
        **fields: Any,
    ) -> "OutputTask":
        """Create a task for the progress object in this output manager.

        Raises:
            Exception

        Returns:
            OutputTask: Object to use to track the progress of the event
        """

        if not self._progress:
            raise Exception

        task_id = self._progress.add_task(
            description=description,
            start=start,
            total=total,
            completed=completed,
            visible=visible,
            **fields,
        )

        return OutputTask(self, task_id)

    def create_output_description(
        self,
        node: Union[
            Resource_Difference, Resource_Reference_Difference, Component_Difference
        ],
    ) -> str:
        """Create a label for a given difference

        Args:
            node (Union[ Resource_Difference, Resource_Reference_Difference, Component_Difference ])

        Raises:
            Exception

        Returns:
            str
        """
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
            raise Exception(
                f"Trying to deploy node {node} but it is not a correct type "
            )

    def _print_component_resources(self, component: ComponentModel) -> None:
        """Print the resources in a component

        Args:
            component (ComponentModel)
        """
        if component.resources is None or not any(component.resources):
            self._console.print(f"        [bold blue] No Resources")
            return

        for resource in component.resources:
            self._console.print(
                f"        [bold blue]{resource.name} ({resource.ruuid})[/bold blue]"
            )

    def _print_component_references(self, component: ComponentModel) -> None:
        """Print the references in a component

        Args:
            component (ComponentModel)
        """

        if component.references is None or not any(component.references):
            self._console.print(f"        [bold blue] No References")
            return

        for reference in component.references:
            self._console.print(
                f"        [bold blue]From {reference.component_name} reference {reference.name} ({reference.ruuid})[/bold blue]"
            )

    def _print_component_differences(
        self, component_diff: Component_Difference
    ) -> None:
        """Print the details in a component difference

        Args:
            component_diff (Component_Difference)
        """
        if component_diff.action_type == Component_Change_Type.UPDATE_NAME:
            self._console.print(
                f"    [bold yellow]Update Name: [/bold yellow][bold blue]{component_diff.previous_name} to {component_diff.new_name} (component)[/bold blue]"
            )
            return

        if component_diff.action_type == Component_Change_Type.UPDATE_IDENTITY:
            self._console.print(
                f"    [bold yellow]Update Identity: [/bold yellow][bold blue]{component_diff.new_name} (component)[/bold blue]"
            )
            return

        if component_diff.action_type == Component_Change_Type.CREATE:
            self._console.print(
                f"    [bold green]Create: [/bold green][bold blue]{component_diff.new_name} (component)[/bold blue]"
            )
            return

        if component_diff.action_type == Component_Change_Type.DELETE:
            self._console.print(
                f"    [bold red]Delete: [/bold red] [bold blue]{component_diff.previous_name} (component)[/bold blue]"
            )
        return

    def _print_component_resource_differences(
        self,
        component_diff: Component_Difference,
        resource_differences: List[Resource_Difference],
    ) -> None:
        """Print details of the resource differences in the component

        Args:
            component_diff (Component_Difference)
            resource_differences (List[Resource_Difference])
        """
        resource_changes = [
            x
            for x in resource_differences
            if x.component_name == component_diff.new_name
            or x.component_name == component_diff.previous_name
        ]

        for resource_diff in resource_changes:
            if resource_diff.action_type == Resource_Change_Type.CREATE:
                self._console.print(
                    f"        [bold green]Create:[/bold green][bold blue] {resource_diff.new_resource.name} ({resource_diff.new_resource.ruuid})[/bold blue]"
                )

            elif resource_diff.action_type == Resource_Change_Type.DELETE:
                self._console.print(
                    f"        [bold red]Delete:[/bold red][bold blue] {resource_diff.previous_resource.name} ({resource_diff.previous_resource.ruuid})[/bold blue]"
                )

            elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
                self._console.print(
                    f"        [bold yellow]Update:[/bold yellow][bold blue] {resource_diff.new_resource.name} ({resource_diff.new_resource.ruuid})[/bold blue]"
                )

            elif resource_diff.action_type == Resource_Change_Type.UPDATE_NAME:
                self._console.print(
                    f"        [bold yellow]Update Name:[/bold yellow][bold blue] from {resource_diff.previous_resource.name} to {resource_diff.new_resource.name} ({resource_diff.new_resource.ruuid})[/bold blue]"
                )

    def _print_component_reference_differences(
        self,
        component_diff: Component_Difference,
        reference_differences: List[Resource_Reference_Difference],
    ) -> None:
        """Print the details in the reference differences

        Args:
            component_diff (Component_Difference)
            reference_differences (List[Resource_Reference_Difference])
        """
        reference_changes = [
            x
            for x in reference_differences
            if x.originating_component_name == component_diff.new_name
        ]

        for reference_diff in reference_changes:
            if reference_diff.action_type == Resource_Reference_Change_Type.CREATE:
                self._console.print(
                    f"        [bold green]Create reference:[/bold green][bold blue] {reference_diff.resource_reference.name} ({reference_diff.resource_reference.ruuid}) from {reference_diff.originating_component_name}[/bold blue]"
                )

            elif reference_diff.action_type == Resource_Reference_Change_Type.DELETE:
                self._console.print(
                    f"        [bold red]Delete reference:[/bold red][bold blue] {reference_diff.resource_reference.name} ({reference_diff.resource_reference.ruuid}) from {reference_diff.originating_component_name}[/bold blue]"
                )


class OutputTask:
    """
    Wrapper around an output that can be used to track long running events. The implementation is as a wrapper around a 'progress task' from the
    rich library. Thus, the api for 'update' and 'start' follows the same pattern as that of a 'task' in the rich library. The print method provides
    access for sending messages to the parent console of this task.
    """

    def __init__(self, output_manager: OutputManager, task_id: TaskID) -> None:
        self._output_manager = output_manager
        self._task_id = task_id

    def print(self, msg: str) -> None:
        """Print a message to the parent output context.

        Args:
            msg (str): message to print
        """
        self._output_manager._console.print(msg)

    def print_error(self, msg: str) -> None:
        """
        Print a message as an error

        Args:
            msg (str): error message
        """
        self.print(f"[bold red]{msg}[/bold red]")

    def update(
        self,
        *args,
        total: float = None,
        completed: float = None,
        advance: float = None,
        description: str = None,
        visible: bool = None,
        refresh: bool = False,
        **fields: Any,
    ) -> None:
        """Update the output tasks

        Args:
            total (float, optional): Defaults to None.
            completed (float, optional): Defaults to None.
            advance (None, optional): Defaults to None.
            description (str, optional): Defaults to None.
            visible (bool, optional): Defaults to None.
            refresh (bool, optional): Defaults to False.
        """
        # self._output_manager._console.print(fields.get('comment'))
        self._output_manager._progress.update(
            self._task_id,
            *args,
            total=total,
            completed=completed,
            advance=advance,
            description=description,
            visible=visible,
            refresh=refresh,
            **fields,
        )

    def start_task(self) -> None:
        """Start the given task progress bar"""
        self._output_manager._progress.start_task(self._task_id)
