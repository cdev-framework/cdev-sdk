from rich.console import Console

# This file outputs things in a pretty way for the CLI
console = Console()

def print_local_diffs(diffs):
    pass
    #if not diffs.get('appends') and not diffs.get('deletes') and not diffs.get('updates'):
    #    console.print("[bold dark_turquoise]No Updates [/bold dark_turquoise]")
#
#
    #if diffs.get('appends'):
    #    for append in diffs.get('appends'):
    #        console.print(f"[bold green]ADDING[/bold green] {append.get('original_path')}: {append.get('local_function_name')} ({append.get('hash')}) -> {append.get('parsed_path')} ")
#
    #if diffs.get('updates'):
    #    for append in diffs.get('updates'):
    #        console.print(f"[bold yellow]UPDATE[/bold yellow] {append.get('original_path')}: {append.get('local_function_name')} ({append.get('hash')}) -> {append.get('parsed_path')} ")
#
    #if diffs.get('deletes'):
    #    for append in diffs.get('deletes'):
    #        console.print(f"[bold red]DELETE[/bold red] {append.get('original_path')}: {append.get('local_function_name')}")
