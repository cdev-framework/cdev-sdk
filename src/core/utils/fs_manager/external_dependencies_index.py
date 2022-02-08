import os
from re import S
from typing import Dict, List, Tuple, Set
from pydantic import BaseModel
from .utils import ExternalDependencyWriteInfo, ModulePackagingInfo, PackageTypes
from rich import print
from itertools import combinations
import math


class ExternalDependencyIndex(BaseModel):
    id: str
    table: Dict[str, int]
    level: int


class weighted_dependency_node:
    def __init__(self, id: str, individual_weight: int) -> None:
        self.id = id
        self.individual_weight = individual_weight
        self.total_weight = 0

        self._parents = set()
        self._children = set()

        self._all_children_flat = set()

    def set_total_weight(self, weight: int):
        self.total_weight = weight

    def add_parent(self, parent: "weighted_dependency_node"):
        self._parents.add(parent)

    def get_parents(self) -> Set["weighted_dependency_node"]:
        return self._parents

    def remove_parent(self, parent: "weighted_dependency_node"):
        if parent in self._parents:
            self._parents.remove(parent)

        else:
            raise Exception

    def add_child(self, child: "weighted_dependency_node"):
        self._children.add(child)
        child.add_parent(self)

        self.add_to_all_children(child.get_all_children())

    def get_children(self) -> Set["weighted_dependency_node"]:
        return self._children

    def get_all_children(self) -> Set["weighted_dependency_node"]:
        return self._all_children_flat

    def add_to_all_children(self, all_children: Set["weighted_dependency_node"]):
        self._all_children_flat.update(all_children)

    def __hash__(self) -> int:
        return int.from_bytes(self.id.encode(), "big")


_depth_to_color = {0: "white", 1: "blue", 2: "yellow", 3: "magenta", 4: "red"}


class weighted_dependency_graph:
    def __init__(self, top_level_modules: List[ModulePackagingInfo]) -> None:
        self._top_level_nodes: List[weighted_dependency_node] = []
        self._id_to_node: Dict[str, weighted_dependency_node] = {}
        self.HEAD = weighted_dependency_node("HEAD", -1)

        (
            self.true_top_level_modules,
            self.referenced_sub_modules,
        ) = self._create_pure_top_level_modules(top_level_modules)

        for top_level_module in self.true_top_level_modules:
            new_top_level_node = self._recursive_add_to_graph(top_level_module)

            if new_top_level_node:
                self._top_level_nodes.append(new_top_level_node)
                self.HEAD.add_child(new_top_level_node)

        for _, node in self._id_to_node.items():
            sub_graph_weight, _ = self._recursive_compute_total_subgraph_weight(
                node, set()
            )
            node.set_total_weight(sub_graph_weight)

    def _create_pure_top_level_modules(
        self, top_level_modules: List[ModulePackagingInfo]
    ) -> Tuple[List[ModulePackagingInfo], List[ModulePackagingInfo]]:
        all_child_modules = set()

        [
            *map(
                lambda x: all_child_modules.update({t.get_id_str() for t in x.flat})
                if x.flat
                else {},
                top_level_modules,
            )
        ]

        true_top_level_modules = []
        referenced_sub_modules = []

        for module_info in top_level_modules:
            if module_info.get_id_str() in all_child_modules:
                referenced_sub_modules.append(module_info)
            else:
                true_top_level_modules.append(module_info)

        return true_top_level_modules, referenced_sub_modules

    def _recursive_add_to_graph(
        self, node_info: ModulePackagingInfo
    ) -> weighted_dependency_node:
        if not node_info.type == PackageTypes.PIP:
            return None

        if not node_info.get_id_str() in self._id_to_node:

            module_individual_weight = get_module_size(node_info.fp)
            new_node = weighted_dependency_node(
                node_info.get_id_str(), module_individual_weight
            )

            if node_info.tree:
                for child_info in node_info.tree:
                    child_node = self._recursive_add_to_graph(child_info)

                    if child_node:
                        new_node.add_child(child_node)

            self._id_to_node[node_info.get_id_str()] = new_node

        else:
            new_node = self._id_to_node.get(node_info.get_id_str())

        return new_node

    def _recursive_compute_total_subgraph_weight(
        self, node: weighted_dependency_node, already_seen: Set[str]
    ) -> Tuple[int, Set[str]]:
        if node.id in already_seen:
            return 0, already_seen

        total_weight = node.individual_weight
        if node.get_children():
            for child in node.get_children():
                (
                    child_weight,
                    already_seen,
                ) = self._recursive_compute_total_subgraph_weight(child, already_seen)
                already_seen.add(child.id)
                total_weight += child_weight

        return total_weight, already_seen

    def print_graph(self):
        total_graph_weight = math.floor(self.get_total_weight() / 1024)
        max_graph_weight = math.floor((250 * 1024))
        percentage_used = math.floor((total_graph_weight / max_graph_weight) * 100)
        print(f"Total dependency size {total_graph_weight} kb ")
        print(f"    {percentage_used}% of max weight: {max_graph_weight} kb ")
        print(self._top_level_nodes)
        for node in self._top_level_nodes:
            total_weight_kb = math.floor(node.total_weight / 1024)
            individual_weight_kb = math.floor(node.individual_weight / 1024)

            print(f"{node.id}  ({total_weight_kb} kb) ({individual_weight_kb} kb)")
            self._recursive_print_graph(node, 0)

    def _recursive_print_graph(self, node: weighted_dependency_node, depth: int):
        for child in node.get_children():

            total_weight_kb = math.floor(child.total_weight / 1024)
            individual_weight_kb = math.floor(child.individual_weight / 1024)

            base_str = f"|[{_depth_to_color.get(depth%5)}]{'-' * depth } {child.id}[/{_depth_to_color.get(depth%5)}] ({total_weight_kb} kb) ({individual_weight_kb} kb) ({len(child.get_parents())})"
            print(base_str)

            self._recursive_print_graph(child, depth + 1)

    def get_total_weight(self) -> int:
        _already_seen_module = set()
        weight = 0

        for node in self._top_level_nodes:
            (
                subtree_unique_weight,
                _already_seen_module,
            ) = self._recursive_compute_weight(node, _already_seen_module)

            weight += subtree_unique_weight

        return weight

    def _recursive_compute_weight(
        self,
        node: weighted_dependency_node,
        already_seen: Set[weighted_dependency_node],
    ) -> Tuple[int, Set[weighted_dependency_node]]:
        weight = 0
        already_seen_module = already_seen
        if node in already_seen:
            # If we have already accounted for this nodes weight then continue
            return (0, already_seen)

        if node.get_children():
            for child in node.get_children():
                (
                    subtree_unique_weight,
                    already_seen_module,
                ) = self._recursive_compute_weight(child, already_seen_module)

                weight += subtree_unique_weight

        weight += node.individual_weight
        already_seen.update([node])

        return weight, already_seen


EXCLUDE_SUBDIRS = {"__pycache__"}


def get_module_size(starting_path: str) -> int:

    if os.path.isfile(starting_path):
        return os.path.getsize(starting_path)

    elif os.path.isdir(starting_path):
        size = 0
        for dirname, subdirs, files in os.walk(starting_path):
            if dirname.split("/")[-1] in EXCLUDE_SUBDIRS:
                continue

            for filename in files:
                full_path = os.path.join(dirname, filename)
                size += os.path.getsize(full_path)

        return size

    else:
        raise Exception


def compute_index(
    dependency_graph: weighted_dependency_graph,
    number_of_top_level_modules_to_remove: int = 2,
) -> Dict:
    index = {}
    _top_level_ids = [x.id for x in dependency_graph._top_level_nodes]
    _start_removals = []

    _start_removals = list(
        combinations(_top_level_ids, number_of_top_level_modules_to_remove)
    )

    for start_removal in _start_removals:
        t = set(start_removal)

        weight_removed = 0

        already_removed = set()
        for top_leaf_child in dependency_graph.HEAD.get_children():
            if top_leaf_child.id in t:
                t2 = t.union(set(["HEAD"]))
                weight_pruned, already_removed = _recursively_compute_removal(
                    top_leaf_child, t2, already_removed
                )
                weight_removed += weight_pruned
            else:
                weight_pruned, already_removed = _recursively_compute_removal(
                    top_leaf_child, t, already_removed
                )
                weight_removed += weight_pruned

        index[start_removal] = weight_removed

    return index


def _recursively_compute_removal(
    current_node: weighted_dependency_node,
    modules_removing: Set[str],
    already_removed: Set[str],
) -> Tuple[int, Set[str]]:
    if not current_node.get_parents():
        raise Exception

    if current_node.id in already_removed:
        # print(f"Already removed {current_node.id}")
        return 0, already_removed

    # All the parent ids and this node must be in the modules to remove if we are going to prune this node
    parent_ids = {x.id for x in current_node.get_parents()}

    remaining_parents = parent_ids.difference(modules_removing)
    # print(f"{current_node.id} has parents {parent_ids} and we are currently removing {modules_removing} -> {remaining_parents} ; {already_removed}")
    if len(remaining_parents) == 0:
        # IF all the parents of this node are in the removing set then remove this module weight
        weight = current_node.individual_weight
        already_removed.add(current_node.id)
        modules_removing.add(current_node.id)

        if current_node.get_children():
            for child in current_node.get_children():
                weight_pruned, already_removed = _recursively_compute_removal(
                    child, modules_removing, already_removed
                )
                weight += weight_pruned

        return weight, already_removed

    else:
        # IF there are other parents remaining then the removing set would not actually cause this module to be removed
        return 0, already_removed
