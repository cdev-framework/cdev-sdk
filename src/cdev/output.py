from typing import List, Tuple
import threading
from rich.console import Console
from rich.prompt import Prompt,Confirm
from rich.progress import Progress, BarColumn, TextColumn


from cdev.utils import hasher   

from cdev.models import Action_Type, Component_State_Difference, Rendered_State
from cdev.utils.environment import get_current_environment

# This file outputs things in a pretty way for the CLI
console = Console()

CAPTURE_OUTPUT = True


def print_local_diffs(diff: Component_State_Difference):
    print(f"[bold magenta] {diff.new_component.name}[/bold magenta]")

    for resource_diff in diff.resource_diffs:

        if resource_diff.action_type == Action_Type.CREATE:
            print(f"    [bold green](CREATE)[/bold green] {resource_diff.new_resource.name}")
        elif resource_diff.action_type == Action_Type.DELETE:
            print(f"    [bold red](DELETE)[/bold red] {resource_diff.previous_resource.name}")
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            print(f"    [bold yellow](UPDATE)[/bold yellow] {resource_diff.new_resource.name}")
        elif resource_diff.action_type == Action_Type.UPDATE_NAME:
            print(f"    [bold yellow](RENAME)[/bold yellow] {resource_diff.previous_resource.name} -> {resource_diff.new_resource.name}")


def print_local_state(state: Rendered_State):
    print("---FULL NEW STATE---")

    for component in state.rendered_components:
        print(f"[bold magenta] {component.name}[/bold magenta]")
        for resource in component.rendered_resources:
            print(f"    [bold blue]{resource.name} ({resource.ruuid})[/bold blue]")


def print_plan(new_state: Rendered_State, diffs: List[Component_State_Difference]):
    print(f"[bold yellow]CURRENT ENVIRONMENT[/bold yellow] -> [bold blue] {get_current_environment()}[/bold blue]")
    
    print_local_state(new_state)

    print(f"---DIFFS---")
    for component_diff in diffs:
        print_local_diffs(component_diff)


def confirm_deployment() -> bool:
    print("")
    rv = Confirm.ask("[bold magenta]Do you want to deploy these changes?[/bold magenta]")
    return rv


def print_deployment_step(action_type: str, msg: str):
    if action_type == 'CREATE':
        print(f"    [bold green](CREATE)[/bold green] {msg}")
    elif action_type == 'UPDATE':
        print(f"    [bold yellow](UPDATE)[/bold yellow] {msg}")
    elif action_type == 'DELETE':
        print(f"    [bold red](DELETE)[/bold red] {msg}")

def print(msg:str) -> None:
    if CAPTURE_OUTPUT:
        add_message(msg)
    else:
        console.print(msg)


####################################################
###### Output capturing for development environment
####################################################
STD_OUT_BUFFER = []

def add_message(msg: str) -> None:
    STD_OUT_BUFFER.append(msg)


def get_messages_from_buffer(start_index: int, end_index: int) -> Tuple[List[str], int]:
    if start_index and end_index:
        messages = STD_OUT_BUFFER[start_index:end_index]
    elif not end_index:
        messages = STD_OUT_BUFFER[start_index:]
    elif not start_index:
        messages = STD_OUT_BUFFER[:end_index]
    else:
        messages = STD_OUT_BUFFER


    return (messages, hasher.hash_list(messages))
