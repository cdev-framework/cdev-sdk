from typing import Dict, List, Set, Tuple
from pydantic import BaseModel
import os
from pydantic.types import DirectoryPath, FilePath
import itertools
from networkx.algorithms.traversal.depth_first_search import dfs_preorder_nodes
import json

from pkg_resources import Distribution
import pkg_resources

import networkx as nx

from core.utils.cache import FileLoadableCache
from core.utils.file_manager import safe_json_write

from .writer import create_archive_and_hash

PACKAGED_CACHE_LOCATION = ".cdev/intermediate/cache/packaged_module_artifacts.json"


class PackagedDistributionInformation(BaseModel):
    project_name: str
    parsed_version: str
    dist_info: DirectoryPath
    dependencies: List[str]

    def __hash__(self):
        return hash(self.project_name)

    def get_modules(self) -> List[str]:
        top_level_fp = os.path.join(self.dist_info, "top_level.txt")
        if top_level_fp == None:
            # Problem when distribution is locally linked... #TODO find more permanent solution
            return []

        if not os.path.isfile(top_level_fp):
            # If not top level file is present, then assume the only top level module available is the project name
            # modified to be python compliant
            return [self.project_name.replace("-", "_")]

        else:
            # Return all the names in the top level file
            with open(top_level_fp) as fh:
                top_level_mod_names = fh.readlines()

            return [x.strip() for x in top_level_mod_names]

    def get_tags(self) -> str:
        wheel_location = os.path.join(self.dist_info, "WHEEL")

        return "-".join(_get_tags_from_wheel(wheel_location))

    def get_all_records(self) -> Set[str]:
        record_file_location = os.path.join(self.dist_info, "RECORD")

        with open(record_file_location, "r") as fh:
            lines = fh.readlines()

        _all_starting_paths = set([x.split(",")[0] for x in lines])

        return set(
            filter(
                lambda x: x[0] != "." and x[-4:] != ".pyc" and "__pycache__" not in x,
                _all_starting_paths,
            )
        )

    def get_base_directory(self) -> DirectoryPath:
        return self.dist_info.parent


def create_packaged_distribution_information(
    package: Distribution, working_set: pkg_resources.WorkingSet
) -> PackagedDistributionInformation:
    """Return the needed metadata about a package.

    Args:
        package (Distribution)

    Returns:
        PackagedDistributionInformation:
    """

    # find the dist info directory that will contain metadata about the package
    dist_dir_location = os.path.join(
        package.location,
        f"{package.project_name.replace('-', '_')}-{package.parsed_version}.dist-info",
    )

    if not os.path.isdir(dist_dir_location):
        # raise Exception(f"No .distinfo found for {package} at {dist_dir_location}")
        return None

    _all_required_packages = package.requires(extras=package.extras)

    _dependencies_names = []
    for _potential_package in _all_required_packages:
        try:
            dependency = working_set.find(_potential_package)
            _dependencies_names.append(dependency.project_name)
        except Exception as e:
            # Since we look for all available dependencies defined in the wheel, we might have an exception if the distribution was not
            # installed with the `extra` tag for certain dependencies
            continue

    return PackagedDistributionInformation(
        project_name=package.project_name,
        parsed_version=str(package.parsed_version),
        dist_info=dist_dir_location,
        dependencies=_dependencies_names,
    )


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


class DistributionEnvironment:
    distributions: PackagedDistributionInformation = []
    _distribution_name_to_dist: Dict[str, PackagedDistributionInformation] = {}
    _all_module_names: Set[str] = set()
    _module_to_dists: Dict[str, Set[PackagedDistributionInformation]] = {}
    _dep_graph: nx.DiGraph = nx.DiGraph()
    _archive_cache: PackagedArtifactCache = None

    @classmethod
    def create_environment(
        cls,
    ) -> None:
        cls.distributions = list(
            filter(
                lambda x: x is not None,
                [
                    create_packaged_distribution_information(
                        x, pkg_resources.working_set
                    )
                    for x in pkg_resources.working_set
                ],
            )
        )

        cls._distribution_name_to_dist = {x.project_name: x for x in cls.distributions}

        cls._all_module_names = set(
            itertools.chain.from_iterable([x.get_modules() for x in cls.distributions])
        )

        for distribution in cls.distributions:
            # Using a list of distributions allows namespace modules to be handled effectively
            # A namespace module will be a module name with more than one distribution
            # Thus if the namespace module is directly used, all distributions in the environment will be included
            for module_name in distribution.get_modules():
                cls._module_to_dists[module_name] = cls._module_to_dists.get(
                    module_name, []
                ) + [distribution]

        for distribution in cls.distributions:
            cls._dep_graph.add_node(distribution)
            for _dependency in distribution.dependencies:
                cls._dep_graph.add_edge(
                    distribution, cls._distribution_name_to_dist.get(_dependency)
                )

        cls._archive_cache = PackagedArtifactCache(PACKAGED_CACHE_LOCATION)

    @classmethod
    def is_module_in_distribution(cls, module_name: str) -> bool:
        return module_name in cls._all_module_names

    @classmethod
    def get_distributions_by_module_name(
        cls, module_name: str
    ) -> Set[PackagedDistributionInformation]:
        if not module_name in cls._module_to_dists:
            raise Exception("Module Name has no Distribution")

        return cls._module_to_dists.get(module_name)

    @classmethod
    def get_optimized_distributions(
        cls, module_names: List[str]
    ) -> Set[PackagedDistributionInformation]:

        _top_level_distributions: Set[PackagedDistributionInformation] = set()
        _optimized_distributions: Set[PackagedDistributionInformation] = set()

        for module_name in module_names:
            _top_level_distributions.update(cls._module_to_dists.get(module_name))

        for top_level_distribution in _top_level_distributions:
            predecessors = set(cls._dep_graph.predecessors(top_level_distribution))

            if len(list(_top_level_distributions.intersection(predecessors))) == 0:
                _optimized_distributions.add(top_level_distribution)

        return _optimized_distributions

    @classmethod
    def get_all_distributions_dependencies(
        cls, distribution: PackagedDistributionInformation
    ) -> Set[PackagedDistributionInformation]:
        return set(dfs_preorder_nodes(cls._dep_graph, distribution))

    @classmethod
    def create_distribution_artifact(
        cls,
        distribution: PackagedDistributionInformation,
        output_directory: str,
        exclude_distributions: Set[str] = set(),
    ) -> Tuple[str, str]:
        if cls._archive_cache.in_cache(distribution.project_name + output_directory):
            return cls._archive_cache.get_from_cache(
                distribution.project_name + output_directory
            )

        _all_distributions = DistributionEnvironment.get_all_distributions_dependencies(
            distribution
        )
        _all_distributions.add(distribution)
        _all_distributions = set(
            filter(
                lambda x: x.project_name not in exclude_distributions,
                _all_distributions,
            )
        )

        _all_records = list(
            itertools.chain.from_iterable(
                [
                    [
                        (
                            os.path.join(x.get_base_directory(), y),
                            os.path.join("python", y),
                        )
                        for y in x.get_all_records()
                    ]
                    for x in _all_distributions
                ]
            )
        )

        archive_fp = os.path.join(
            output_directory,
            f"{distribution.project_name}-{distribution.get_tags()}.zip",
        )
        archive_hash = create_archive_and_hash(_all_records, archive_fp)

        cls._archive_cache.update_cache(
            distribution.project_name + output_directory, (archive_fp, archive_hash)
        )
        cls._archive_cache.dump_to_file()

        return archive_fp, archive_hash


def _get_tags_from_wheel(wheel_info_location: FilePath) -> List[str]:
    """Get the tags information from a wheels file

    Args:
        wheel_info_location (FilePath)

    Returns:
        List[str]: tags
    """
    with open(wheel_info_location) as fh:
        lines = fh.readlines()

        # https://www.python.org/dev/peps/pep-0425/
        # if it is not pure it should only have one tag
        # We are going ot check the tags of the package to make sure it is compatible with the target deployment platform
        tags = (
            [x.split(":")[1] for x in lines if x.split(":")[0] == "Tag"][0]
            .strip()
            .split("-")
        )

        return tags
