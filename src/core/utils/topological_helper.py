"""Utilities to help work with the Resource Dependency Graph.

One of the core components of the Cdev Core framework is the Resource Dependency Graph. This graph is implemented
using the `networkx` packages as it provides helpful utilities for working with graph data structures.
"""

from concurrent.futures import ThreadPoolExecutor, Future
from enum import Enum

from networkx.classes.digraph import DiGraph
from networkx.classes.reportviews import NodeView


from typing import Callable, Dict, List, Set, Tuple
from time import sleep

from core.constructs.resource import (
    Resource_Change_Type,
    Resource_Reference_Change_Type,
    ResourceModel,
    Resource_Difference,
    Resource_Reference_Difference,
)
from core.constructs.cloud_output import OutputType, cloud_output_model
from core.constructs.components import Component_Change_Type, Component_Difference
from core.constructs.output_manager import OutputTask
from core.constructs.models import frozendict

from core.utils.operations import concatenate

deliminator = "+"


def find_parents(resource: ResourceModel) -> Tuple[List, List]:
    """Find any parents resources via any linked Cloud Output Models

    If a resource contains the cloud output of another resource, the relationship
    needs to be identified as a parent-child relationship with the Resource Dependency
    Graph.

    Args:
        resource (ResourceModel): Resource to look for any parents with

    Returns:
        Tuple[
            parent_resources: List[Tuple[ruuid, name]]
            parent_resources: List[Tuple[ruuid, name]]
        ]
    """
    resource_as_obj = resource.dict()

    cloud_outputs = find_cloud_output(resource_as_obj)

    parent_resources = [
        (x.ruuid, x.name) for x in cloud_outputs if x.type == OutputType.RESOURCE
    ]
    parent_references = [
        (x.ruuid, x.name) for x in cloud_outputs if x.type == OutputType.REFERENCE
    ]

    return parent_resources, parent_references


def find_cloud_output(obj: dict) -> List[cloud_output_model]:
    """Given an object representing the cloud output generate all the parent cloud output models

    Args:
        obj (dict)

    Returns:
        List[cloud_output_model]
    """

    rv = _recursive_find_output(obj)

    return list(set(rv))


def _recursive_find_output(obj) -> List[cloud_output_model]:
    if isinstance(obj, frozendict) or isinstance(obj, dict):
        if "id" in obj and obj.get("id") == "cdev_cloud_output":
            return [cloud_output_model(**obj)]
        else:
            return concatenate([_recursive_find_output(v) for _, v in obj.items()])

    elif isinstance(obj, frozenset) or isinstance(obj, list):
        return concatenate([_recursive_find_output(x) for x in obj])

    else:
        return []


def generate_sorted_resources(
    differences: Tuple[
        List[Component_Difference],
        List[Resource_Difference],
        List[Resource_Reference_Difference],
    ]
) -> DiGraph:
    """Given the tuple of all differences, generate a DiGraph representing a topologically valid way of applying the changes.

    Args:
        differences (Tuple[ List[Component_Difference], List[Resource_Difference], List[Resource_Reference_Difference], ]): _description_

    Raises:
        Exception

    Returns:
        DiGraph
    """
    # nx graphs work on the element level by using the __hash__ of objects added to the graph, so all the elements added to the graph should be a pydantic Model with
    # the 'frozen' feature set
    change_dag = DiGraph()

    component_differences = differences[0]
    resource_differences = differences[1]
    reference_differences = differences[2]

    component_ids = {
        _create_component_id(x.new_name): x
        for x in component_differences
        if x.action_type == Component_Change_Type.CREATE
        or x.action_type == Component_Change_Type.UPDATE_NAME
        or x.action_type == Component_Change_Type.UPDATE_IDENTITY
    }
    component_ids.update(
        {
            _create_component_id(x.previous_name): x
            for x in component_differences
            if x.action_type == Component_Change_Type.DELETE
        }
    )

    resource_ids = {
        _create_resource_id(
            x.component_name, x.new_resource.ruuid, x.new_resource.name
        ): x
        for x in resource_differences
        if x.action_type == Resource_Change_Type.UPDATE_IDENTITY
        or x.action_type == Resource_Change_Type.CREATE
        or x.action_type == Resource_Change_Type.UPDATE_NAME
    }
    resource_ids.update(
        {
            _create_resource_id(
                x.component_name, x.previous_resource.ruuid, x.previous_resource.name
            ): x
            for x in resource_differences
            if x.action_type == Resource_Change_Type.DELETE
        }
    )

    reference_ids = {
        _create_reference_id(
            x.originating_component_name,
            x.resource_reference.component_name,
            x.resource_reference.ruuid,
            x.resource_reference.name,
        ): x
        for x in reference_differences
    }

    for _, component in component_ids.items():
        change_dag.add_node(component)

    for _, resource in resource_ids.items():
        change_dag.add_node(resource)

        component_id = _create_component_id(resource.component_name)

        if component_id in component_ids:
            if (
                resource.action_type == Resource_Change_Type.DELETE
                and component_ids.get(component_id).action_type
                == Component_Change_Type.DELETE
            ):
                # Since these are both deletes, it should happen in the reverse order
                change_dag.add_edge(resource, component_ids.get(component_id))

            else:
                change_dag.add_edge(component_ids.get(component_id), resource)
        else:
            raise Exception(
                f"There should always be a change in a component for a resource change {resource}"
            )

        parent_resources, parent_references = (
            find_parents(resource.new_resource)
            if resource.action_type != Resource_Change_Type.DELETE
            else find_parents(resource.previous_resource)
        )

        if not parent_resources and not parent_references:
            continue

        for parent_ruuid, parent_name in parent_resources:
            # Parent resources must be in the same component

            # Cloud outputs of a resource will always be from the same component
            parent_resource_id = _create_resource_id(
                resource.component_name, parent_ruuid, parent_name
            )

            if parent_resource_id in resource_ids:
                if resource.action_type == Resource_Change_Type.DELETE:
                    # Since this is a delete, it should happen in the reverse order
                    change_dag.add_edge(resource, resource_ids.get(parent_resource_id))

                else:
                    # Make this resource change a child of the parent resource change
                    change_dag.add_edge(resource_ids.get(parent_resource_id), resource)

        for parent_ruuid, parent_name in parent_references:
            parent_reference_id = _create_reference_id(
                resource.component_name,
                resource.component_name,
                parent_ruuid,
                parent_name,
            )

            if parent_reference_id in reference_ids:
                if resource.action_type == Resource_Change_Type.DELETE:
                    # Since this is a delete, it should happen in the reverse order
                    change_dag.add_edge(resource, resource_ids.get(parent_reference_id))

                else:
                    change_dag.add_edge(resource_ids.get(parent_reference_id), resource)

    for _, reference in reference_ids.items():
        change_dag.add_node(reference)

        # Reference changes should be a child to an Update Identity component diff
        originating_component_id = _create_component_id(
            reference.originating_component_name
        )

        if originating_component_id in component_ids:
            change_dag.add_edge(component_ids.get(originating_component_id), reference)

        else:
            raise Exception(
                f"There should always be a change in a component for a reference change {resource}"
            )

        # Reference change should also be a child to any change to the referenced resource
        resource_id = _create_resource_id(
            reference.resource_reference.component_name,
            reference.resource_reference.ruuid,
            reference.resource_reference.name,
        )
        if resource_id in resource_ids:
            # If there is also a change to the component this reference is apart of then the changes need to be ordered
            if reference.action_type == Resource_Reference_Change_Type.CREATE:
                if (
                    resource_ids.get(resource_id).action_type
                    == Resource_Change_Type.DELETE
                ):
                    # We can not create a reference if that resource is currently being destroyed.
                    raise Exception(
                        f"Trying to reference a resource that is being deleted {reference} -> {resource_id}"
                    )

                # Since the reference is being created, we should perform the operation after the changes to the underlying resource
                change_dag.add_edge(resource_ids.get(resource_id), reference)

            else:
                change_dag.add_edge(reference, resource_ids.get(resource_id))

        else:
            # Since the original resource is not in the change set, it should be checked to be sure that it is accessible from the backend
            pass

    return change_dag


def _create_component_id(component_name: str) -> str:
    """Create the id for a given component

    Component Differences will be identified by the key component<deliminator><component_name>

    Args:
        component_name (str)

    Returns:
        str
    """
    return f"component{deliminator}{component_name}"


def _create_resource_id(component_name: str, ruuid: str, name: str) -> str:
    """Create id for a given resource

    Resource Differences will be identified by the key resource<deliminator><ruuid><deliminator><name>

    Args:
        component_name (str): component the resource is in
        ruuid (str): resource type id
        name (str): name of the resource

    Returns:
        str
    """
    return (
        f"resource{deliminator}{component_name}{deliminator}{ruuid}{deliminator}{name}"
    )


def _create_reference_id(
    originating_component_name: str, component_name: str, ruuid: str, name: str
) -> str:
    """Create id for a given reference

    Reference Differences will be identified by the key reference<deliminator><ruuid><deliminator><name>

    Args:
        originating_component_name (str): component original resource resides in
        component_name (str): component the reference is in
        ruuid (str): resource type id
        name (str): name of the reference

    Returns:
        str: _description_
    """
    return f"reference{deliminator}{originating_component_name}{deliminator}{component_name}{deliminator}{ruuid}{deliminator}{name}"


class node_state(str, Enum):
    UNPROCESSED = "UNPROCESSED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"
    PARENT_ERROR = "PARENT_ERROR"


def topological_iteration(
    dag: DiGraph,
    process: Callable[[NodeView], None],
    failed_parent_handler: Callable[[NodeView], None] = None,
    thread_count: int = 1,
    interval: float = 0.3,
    pass_through_exceptions: bool = False,
) -> None:
    """Execute the `process` over a DAG in a topologically constrained way.

    This means that the `process` will not be executed on a node until the `process` has been executed on all parents of that node.

    If the `process` throws an Exception when executing on a Node, then any child nodes will not be executed (if provided, the
    failed_parent_handler will be executed on the child nodes).

    This iteration supports multiple threads via the `thread_count` param. Multiple threads can speed up the total iteration time if the `process`
    is not CPU bound and there are non-dependant paths through the DAG. Note that the `process` provided should be thread safe when using multiple threads.

    Args:
        dag (DiGraph): The graph to execute over.
        process (Callable[[NodeView], None]): The function to call on each Node.
        failed_parent_handler (Callable[[NodeView], None], optional): A function to call on Nodes that do not execute because a parent failed.
        thread_count (int, optional): [description]. Defaults to 1
        interval (float, optional): Interval (in seconds) to poll threads for completion. Defaults to .3
    """

    all_children: Set[NodeView] = set(x[1] for x in dag.edges)
    all_nodes: Set[NodeView] = set(x for x in dag.nodes())

    # starting nodes are those that have no parents
    starting_nodes = all_nodes - all_children

    nodes_to_process: list[NodeView] = []
    nodes_to_process.extend(starting_nodes)

    _processing_future_to_resource: Dict[Future, NodeView] = {}

    # Keep track of the state of all nodes to determine when the entire DAG has been traversed
    _node_to_state: Dict[NodeView, node_state] = {
        x: node_state.UNPROCESSED for x in all_nodes
    }

    executor = ThreadPoolExecutor(thread_count)

    # While any node is unprocessed or still processing
    while any(
        _node_to_state.get(x) == node_state.UNPROCESSED
        or _node_to_state.get(x) == node_state.PROCESSING
        for x in all_nodes
    ):

        # Pull any ready nodes to be processed and add them to the thread pool
        for _ in range(0, len(nodes_to_process)):
            node_to_process = nodes_to_process.pop(0)
            future = executor.submit(process, node_to_process)

            _processing_future_to_resource[future] = node_to_process
            _node_to_state[node_to_process] = node_state.PROCESSING

        # Check if any of the futures are finished and then make decisions about their children from the rv of the future
        for fut, node in _processing_future_to_resource.copy().items():
            # Note python throws runtime error if you change a dict size while iterating so use a copy for now.
            # TODO: Check if there is a more optimized way to do this

            if not fut.done():
                # Still processing
                continue

            try:
                result = fut.result()

                # No exceptions raised so process completed correctly
                _node_to_state[node] = node_state.PROCESSED

                children = dag.successors(node)

                for child in children:
                    # If any of the parents of the child have not been processed, than the child node is not ready to be processed
                    if any(
                        not _node_to_state.get(x) == node_state.PROCESSED
                        for x in dag.predecessors(child)
                    ):
                        continue

                    nodes_to_process.append(child)

            except Exception as e:
                # Since this returned a error need to mark all children as unable to deploy
                _node_to_state[node] = node_state.ERROR

                # mark an descdents of this node as unable to process
                _recursively_mark_parent_failure(
                    _node_to_state, dag, node, handler=failed_parent_handler
                )

                if pass_through_exceptions:
                    raise e

            # Remove the future from the dictionary
            _processing_future_to_resource.pop(fut)

        sleep(interval)

    executor.shutdown()


def _recursively_mark_parent_failure(
    _node_to_state: Dict[NodeView, node_state],
    dag: DiGraph,
    parent_node: NodeView,
    handler: Callable[[NodeView, OutputTask], None] = None,
    pass_through_exceptions: bool = False,
) -> None:
    """Recursively mark all descendent of a failure

    Args:
        _node_to_state (Dict[NodeView, node_state]): mapping between nodes and final states
        dag (DiGraph): graph
        parent_node (NodeView): starting node
        handler (Callable[[NodeView, OutputTask], None], optional): function to call on children. Defaults to None.
        pass_through_exceptions (bool, optional): suppress any additional errors. Defaults to False.

    Raises:
        Exception
    """

    if parent_node not in _node_to_state:
        raise Exception(
            f"trying to mark node ({parent_node}) but cant not find it in given dict"
        )

    children = dag.successors(parent_node)

    for child in children:

        if child not in _node_to_state:
            raise Exception(
                f"trying to mark node ({child}) but cant not find it in given dict"
            )

        _node_to_state[child] = node_state.PARENT_ERROR

        if handler:
            # Call a handler that does extra busines logic for items that fail because of their parent
            try:
                handler(child)

            except Exception as e:
                # handler threw exception but we should continue

                if pass_through_exceptions:
                    raise e

        _recursively_mark_parent_failure(_node_to_state, dag, child)
