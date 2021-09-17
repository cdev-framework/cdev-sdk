from typing import List
import threading
from rich.console import Console
from rich.prompt import Prompt,Confirm
from rich.progress import Progress, BarColumn, TextColumn

from time import sleep

from cdev.models import Action_Type, Component_State_Difference, Rendered_State
from cdev.utils.environment import get_current_environment

# This file outputs things in a pretty way for the CLI
console = Console()

def print_local_diffs(diff: Component_State_Difference):
    console.print(f"[bold magenta] {diff.new_component.name}[/bold magenta]")

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
    console.print("---FULL NEW STATE---")

    for component in state.rendered_components:
        console.print(f"[bold magenta] {component.name}[/bold magenta]")
        for resource in component.rendered_resources:
            console.print(f"    [bold blue]{resource.name} ({resource.ruuid})[/bold blue]")


def print_plan(new_state: Rendered_State, diffs: List[Component_State_Difference]):
    console.print(f"[bold yellow]CURRENT ENVIRONMENT[/bold yellow] -> [bold blue] {get_current_environment()}[/bold blue]")
    
    print_local_state(new_state)

    console.print(f"---DIFFS---")
    for component_diff in diffs:
        print_local_diffs(component_diff)


def confirm_deployment() -> bool:
    console.print("")
    rv = Confirm.ask("[bold magenta]Do you want to deploy these changes?[/bold magenta]")
    return rv


def print_deployment_step(action_type: str, msg: str):
    if action_type == 'CREATE':
        console.print(f"    [bold green](CREATE)[/bold green] {msg}")
    elif action_type == 'UPDATE':
        console.print(f"    [bold yellow](UPDATE)[/bold yellow] {msg}")
    elif action_type == 'DELETE':
        console.print(f"    [bold red](DELETE)[/bold red] {msg}")

def print(msg:str) -> None:
    console.print(msg)


####################################################
###### Output capturing for development environment
####################################################

def start_capturing_console():
    console.begin_capture()

def get_current_captured_logs() -> str:
    new_output = console.end_capture()
    print(new_output)
    console.begin_capture()
    return new_output

def end_capturing_console():
    return console.end_capture()