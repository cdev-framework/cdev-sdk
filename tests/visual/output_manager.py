from networkx.classes.reportviews import NodeView
from networkx.algorithms.dag import topological_sort
from rich.console import Console, ConsoleOptions
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    SpinnerColumn,
)
from time import sleep
from typing import Callable, Dict, List, Tuple


from core.constructs.output_manager import OutputManager, OutputTask


from tests.core.sample_data import (
    simple_components,
    simple_differences_for_topo_sort,
    simple_change_dag,
)

om = OutputManager()


def print_header():
    om.print_header("1234")


def print_local_state():
    om.print_local_state([x.render() for x in simple_components()])


def print_differences():
    om.print_state_differences(simple_differences_for_topo_sort()[0])


def sample_cloud_deploy():
    console = Console()
    dag, _ = simple_change_dag()

    messages = [
        "Starting Deployment",
        "Deploying on Cloud :cloud:",
        "Completing transaction with Backend",
    ]

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(finished_style="white"),
        TimeElapsedColumn(),
        TextColumn("{task.fields[comment]}"),
        console=console,
    ) as progress:
        manager = OutputManager(console, progress)

        all_nodes_sorted: List[NodeView] = [x for x in topological_sort(dag)]
        _node_to_output_task: Dict[NodeView, OutputTask] = {
            x: manager.create_task(
                manager.create_output_description(x),
                start=False,
                total=10,
                comment="Waiting to deploy",
            )
            for x in all_nodes_sorted
        }

        for node in all_nodes_sorted:
            _node_to_output_task[node].start_task()

            for i in range(0, 3):
                _node_to_output_task[node].update(advance=3, comment=messages[i])
                sleep(1)

            _node_to_output_task[node].update(
                completed=10, comment="Completed :white_check_mark:"
            )


functions_to_run: List[Tuple[Callable, str]] = [
    (print_header, "Output Manger Header"),
    (print_local_state, "Local State Output"),
    (print_differences, "Differences in State"),
    (sample_cloud_deploy, "Cloud deployment"),
]

if __name__ == "__main__":
    for function, title in functions_to_run:
        print("")
        print(title)
        print("---------------------")
        function()
