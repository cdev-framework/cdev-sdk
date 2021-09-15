from typing import List
from rich.console import Console

from cdev.models import Action_Type, Component_State_Difference, Rendered_State
from cdev.utils.environment import get_current_environment

# This file outputs things in a pretty way for the CLI
console = Console()

def print_local_diffs(diff: Component_State_Difference):
    console.print(f"[bold purple] {diff.new_component.name}[/bold purple]")

    for resource_diff in diff.resource_diffs:

        if resource_diff.action_type == Action_Type.CREATE:
            console.print(f"    [bold green](CREATE)[/bold green] {resource_diff.new_resource.name}")
        elif resource_diff.action_type == Action_Type.DELETE:
            console.print(f"    [bold red](DELETE)[/bold red] {resource_diff.previous_resource.name}")
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            console.print(f"    [bold yellow](UPDATE)[/bold yellow] {resource_diff.new_resource.name}")
        elif resource_diff.action_type == Action_Type.UPDATE_NAME:
            console.print(f"    [bold yellow](RENAME)[/bold yellow] {resource_diff.previous_resource.name} -> {resource_diff.new_resource.name}")


def print_local_state(state: Rendered_State):
    console.print("---NEW STATE---")

    for component in state.rendered_components:
        console.print(f"[bold purple] {component.name}[/bold purple]")
        for resource in component.rendered_resources:
            console.print(f"    [bold blue]{resource.name} ({resource.ruuid})[/bold blue]")


def print_plan(new_state: Rendered_State, diffs: List[Component_State_Difference]):
    console.print(f"[bold yellow]CURRENT ENVIRONMENT[/bold yellow] -> [bold blue] {get_current_environment()}[/bold blue]")
    
    print_local_state(new_state)

    console.print(f"---DIFFS---")
    for component_diff in diffs:
        print_local_diffs(component_diff)