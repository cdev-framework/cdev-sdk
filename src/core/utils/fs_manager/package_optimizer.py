from pydantic import BaseModel, DirectoryPath, FilePath
from typing import Dict, List, Set, Tuple
import os

from . import writer
from .module_types import ModuleInfo, PackagedModuleInfo


class LayerDependency(BaseModel):
    pass


class SingleLayerDependency(LayerDependency):
    top_module: ModuleInfo
    dependencies: List[ModuleInfo]


def create_packaged_module_artifacts(
    pkged_mods: List[PackagedModuleInfo],
    pkged_module_dependencies_data: Dict[str, List[str]],
    base_output_directory: DirectoryPath,
    platform_filter: Set[str] = {},
    exclude_subdirectories: Set[str] = {},
    layers_available: int = 5,
) -> List[Tuple[FilePath, str]]:
    """Full function that can be turned into a 'packaged_module_packager_type' to be used in the
    serverless function optimizer.

    Args:
        pkged_mods (List[PackagedModuleInfo]): modules to package.
        pkged_module_dependencies_data (Dict[str, List[str]]): data representing the dependency info between modules.
        base_output_directory (DirectoryPath): base directory of final artifacts.
        platform_filter (Set[str], optional): packages not needed for a particular deployment platform. Defaults to {}.
        exclude_subdirectories (Set[str], optional): Subdirectories to ignore when packaging. Defaults to {}.
        layers_available (int, optional): Max number of layers to create. Defaults to 5.

    Returns:
        List[Tuple[FilePath, str]]: _description_
    """
    optimized_packages = _create_optimal_packaged_modules(
        pkged_mods, pkged_module_dependencies_data, platform_filter, layers_available
    )

    return [
        (
            os.path.join(base_output_directory, _create_single_layer_name(x)),
            writer.create_layer_archive(
                [x.top_module, *x.dependencies],
                os.path.join(base_output_directory, _create_single_layer_name(x)),
                exclude_subdirectories=exclude_subdirectories,
            ),
        )
        for x in optimized_packages
    ]


def _create_single_layer_name(layer: SingleLayerDependency) -> str:
    return f"{layer.top_module.module_name}-{layer.top_module.tag}.zip"


def _create_optimal_packaged_modules(
    modules: List[PackagedModuleInfo],
    pkged_module_dependencies_data: Dict[str, List[str]],
    platform_filter: Set[str] = {},
    available_slots: int = 5,
) -> List[SingleLayerDependency]:
    """Given the list of all packaged modules needed for a serverless function, return a List of LayerDependencies
    representing the optimal way to package the modules.

    Args:
        modules (List[PackagedModuleInfo]): _description_
        pkged_module_dependencies_data (Dict[str, List[str]]): _description_
        available_slots (int, optional): _description_. Defaults to 5.

    Raises:
        Exception: _description_

    Returns:
        List: _description_
    """
    _module_name_to_info = {x.module_name: x for x in modules}
    _used_module_names = set([x.module_name for x in modules])

    top_level_module_names = _find_all_top_modules(
        _used_module_names, pkged_module_dependencies_data
    )

    needed_top_level_names = _used_module_names.intersection(
        top_level_module_names
    ).difference(platform_filter)

    if len(needed_top_level_names) <= available_slots:
        return [
            SingleLayerDependency(
                top_module=_module_name_to_info.get(x),
                dependencies=[
                    _module_name_to_info.get(y)
                    for y in pkged_module_dependencies_data.get(x)
                ],
            )
            for x in needed_top_level_names
        ]

    else:
        raise Exception(f"Too many modules and no composite layer optimizer is present")


def _find_all_top_modules(
    used_modules: Set[str], pkged_module_dependencies_data: Dict[str, List[str]]
) -> Set[str]:
    """Given the dependency information about packaged modules, find the modules
    that do are not a dependency for another module. This represent the set of modules
    that must explicitly be packaged if used by a function.

    Args:
        pkged_module_dependencies_data (Dict[str, List[str]])

    Returns:
        Set[str]: Modules that are not a dependency for another module
    """

    all_modules_names = set(used_modules)

    for _, dependencies in list(
        filter(lambda k: k[0] in used_modules, pkged_module_dependencies_data.items())
    ):

        for dependency in dependencies:
            try:
                all_modules_names.remove(dependency)
            except Exception as e:
                pass

    return all_modules_names
