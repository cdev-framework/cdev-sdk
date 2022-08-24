from pydantic import BaseModel, DirectoryPath, FilePath
from typing import Dict, List, Set, Tuple
import os
import json

from core.utils.cache import Cache, FileLoadableCache
from core.utils.file_manager import safe_json_write
from core.utils.hasher import hash_list
from core.utils.paths import create_path_from_workspace


from . import writer
from .module_types import ModuleInfo, PackagedModuleInfo

ARTIFACT_CACHE_NAME = "packaged_module_artifacts"
ARTIFACT_CACHE_FILENAME = "packaged_module_artifacts.json"

OPTIMIZED_MODULES_CACHE_NAME = "optimized_modules"
OPTIMIZED_MODULES_CACHE_FILENAME = "optimized_modules.json"

deliminator = "-"


class LayerDependency(BaseModel):
    pass


class SingleLayerDependency(LayerDependency):
    top_module: PackagedModuleInfo
    dependencies: List[PackagedModuleInfo]


class OptimalModulesCache(FileLoadableCache):
    """Implementation of FileLoadableCache designed to cache the results of the optimal packaged module computation."""

    def dump_to_file(self) -> None:

        json_safe_data = {
            k: [vv.dict() for vv in v] for k, v in self._cache_data.items()
        }
        safe_json_write(json_safe_data, self.fp)

    def _load_from_file(self, fp: FilePath) -> Dict:
        if not os.path.isfile(self.fp):
            return {}

        try:
            with open(self.fp) as fh:
                raw_cache_data: Dict[str, Dict] = json.load(fh)
        except Exception as e:
            # Could not load the file so just return an empty cache
            return {}

        validated_data = {}

        for key, val in raw_cache_data.items():
            try:
                serialized_data = [SingleLayerDependency(**x) for x in val]
            except Exception as e:
                continue

            validated_data[key] = serialized_data

        return validated_data


class PackagedArtifactCache(FileLoadableCache):
    """Implementation of FileLoadableCache designed to cache the results of the create packaged module archive action"""

    def dump_to_file(self) -> None:
        safe_json_write(self._cache_data, self.fp)

    def _load_from_file(self, fp: FilePath) -> Dict:
        if not os.path.isfile(fp):
            return {}

        try:
            with open(fp) as fh:
                raw_cache_data: Dict[str, Tuple[FilePath, str]] = json.load(fh)
        except Exception as e:
            # Could not load the file so just return an empty cache
            return {}

        validated_data = {}

        for key, val in raw_cache_data.items():
            artifact_fp, _ = val

            if os.path.isfile(artifact_fp):
                # Only actually load cache values where the artifact is present on the current filesystem
                validated_data[key] = val

        return validated_data


def load_optimal_modules_cache(
    base_cache_location: DirectoryPath,
) -> OptimalModulesCache:
    """Load the optimal module cache from data in the provided directory

    Args:
        base_cache_location (DirectoryPath): base directory to look for already generated cache data

    Raises:
        Exception: invalid directory

    Returns:
        OptimalModulesCache
    """
    if not os.path.isdir(base_cache_location):
        create_path_from_workspace(base_cache_location)

    cache_location = os.path.join(base_cache_location, OPTIMIZED_MODULES_CACHE_FILENAME)

    cache = OptimalModulesCache(cache_location)

    return cache


def load_packaged_artifact_cache(
    base_cache_location: DirectoryPath,
) -> PackagedArtifactCache:
    """Load the packaged module artifacts cache from data in the provided directory

    Args:
        base_cache_location (DirectoryPath): base directory to look for already generated cache data

    Raises:
        Exception: invalid directory

    Returns:
        PackagedArtifactCache: _description_
    """
    if not os.path.isdir(base_cache_location):
        create_path_from_workspace(base_cache_location)

    cache_location = os.path.join(base_cache_location, ARTIFACT_CACHE_FILENAME)

    cache = PackagedArtifactCache(cache_location)

    return cache


def create_packaged_module_artifacts(
    pkged_mods: List[PackagedModuleInfo],
    pkged_module_dependencies_data: Dict[str, List[str]],
    base_output_directory: DirectoryPath,
    platform_filter: Set[str] = {},
    exclude_subdirectories: Set[str] = {},
    layers_available: int = 5,
    optimal_module_cache: Cache = None,
    packaged_artifact_cache: Cache = None,
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
        List[Tuple[FilePath, str]]: List of Tuples of (artifact_path, artifact_hash)
    """
    optimized_packages = _create_optimal_packaged_modules(
        pkged_mods,
        pkged_module_dependencies_data,
        platform_filter,
        layers_available,
        optimal_module_cache,
    )

    return [
        (
            os.path.join(base_output_directory, _create_single_layer_name(x)),
            writer.create_layer_archive(
                [x.top_module, *x.dependencies],
                os.path.join(base_output_directory, _create_single_layer_name(x)),
                exclude_subdirectories=exclude_subdirectories,
                cache=packaged_artifact_cache,
            ),
        )
        for x in optimized_packages
    ]


def _create_single_layer_name(layer: SingleLayerDependency) -> str:
    """Helper function for defining the name of a SingleLayerDependency

    Args:
        layer (SingleLayerDependency): provided layer

    Returns:
        str: name
    """
    return f"{layer.top_module.module_name}-{layer.top_module.tag}.zip"


def _create_cache_key(
    modules: List[PackagedModuleInfo], platform_filter: Set[str], available_slots: int
) -> str:
    """Helper function for creating the hash key from the input to `_create_optimal_packaged_modules`

    Args:
        modules (List[PackagedModuleInfo]): all available modules
        platform_filter (Set[str]): packages that are by default available on a platform
        available_slots (int): amount of slots available

    Returns:
        str: cache key
    """
    _ids = [
        *[f"{x.module_name}{deliminator}{x.tag}" for x in modules],
        *platform_filter,
    ]
    _ids.sort()
    _ids.append(str(available_slots))

    return hash_list(_ids)


def _create_optimal_packaged_modules(
    modules: List[PackagedModuleInfo],
    pkged_module_dependencies_data: Dict[str, List[str]],
    platform_filter: Set[str] = {},
    available_slots: int = 5,
    cache: Cache = None,
) -> List[SingleLayerDependency]:
    """Given the list of all packaged modules needed for a serverless function, return a List of LayerDependencies
    representing the optimal way to package the modules.

    Args:
        modules (List[PackagedModuleInfo]): all available modules
        pkged_module_dependencies_data (Dict[str, List[str]]): data encoding dependencies between modules.
        platform_filter (Set[str]): packages that are by default available on a platform
        available_slots (int): amount of slots available
        cache (Optional[Cache]): a Cache to speed up operation

    Raises:
        Exception: Too many top level modules

    Returns:
        List[SingleLayerDependency]
    """
    if cache:
        cache_key = _create_cache_key(modules, platform_filter, available_slots)

        if cache.in_cache(cache_key):
            return cache.get_from_cache(cache_key)

    _module_name_to_info = {x.module_name: x for x in modules}
    _used_module_names = set([x.module_name for x in modules])

    top_level_module_names = _find_all_top_modules(
        _used_module_names, pkged_module_dependencies_data
    )

    needed_top_level_names = _used_module_names.intersection(
        top_level_module_names
    ).difference(platform_filter)

    if len(needed_top_level_names) <= available_slots:
        rv = [
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

    if cache:
        cache.update_cache(cache_key, rv)

    return rv


def _find_all_top_modules(
    used_modules: Set[str], pkged_module_dependencies_data: Dict[str, List[str]]
) -> Set[str]:
    """Given the dependency information about packaged modules, find the modules
    that do are not a dependency for another module. This represent the set of modules
    that must explicitly be packaged if used by a function.

    Args:
        used_modules (Set[str]): modules directly imported
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
