import docker
import json
import os
from pkg_resources import Distribution
import re
from typing import List

from core.constructs.workspace import Workspace


from .utils import (
    PackageTypes,
    ModulePackagingInfo,
    lambda_python_environment,
    parse_requirement_line,
    CONTAINER_NAMES,
    environment_to_architecture_suffix
)

from core.utils.logger import log


def docker_available() -> bool:
    return True

has_run_container = False
build_container = None


class DockerDownloadCache:
    """
    Naive cache implentation for know which files have been downloaded.
    """

    def __init__(self, cache_location: str) -> None:
        self._cache_location = os.path.join(cache_location, "cache.json")
        self._downloads_locations = os.path.join(cache_location, "downloads")

        if not os.path.isdir(self._downloads_locations):
            os.mkdir(self._downloads_locations)


        if not os.path.isfile(self._cache_location):
            self._cache = {
                lambda_python_environment.py37: {},
                lambda_python_environment.py38_x86_64: {},
                lambda_python_environment.py38_arm64: {},
                lambda_python_environment.py39_x86_64: {},
                lambda_python_environment.py39_arm64: {},
                lambda_python_environment.py3_x86_64: {},
                lambda_python_environment.py3_arm64: {},
            }

        else:
            with open(self._cache_location) as fh:
                self._cache = json.load(fh)

        self._cache_dirs = {
            lambda_python_environment.py37: "py37",
            lambda_python_environment.py38_x86_64: "py38x8664",
            lambda_python_environment.py38_arm64: "py38arm64",
            lambda_python_environment.py39_x86_64: "py39x8664",
            lambda_python_environment.py39_arm64: "py39arm64",
            lambda_python_environment.py3_x86_64: "py3x8664",
            lambda_python_environment.py3_arm64: "py3arm64",
        }

    def find_item(self, environment: lambda_python_environment, id: str):
        raw_data = self._cache.get(environment).get(id)
        if raw_data:
            return [ModulePackagingInfo(**x) for x in raw_data]
        else:
            None

    def add_item(
        self,
        environment: lambda_python_environment,
        id: str,
        item: ModulePackagingInfo,
    ):
        self._cache[environment][id] = item

        with open(self._cache_location, "w") as fh:
            json.dump(self._cache, fh, indent=4)

    def get_packaging_dir(self, environment: lambda_python_environment):
        FULL_DIR = os.path.join(self._downloads_locations, self._cache_dirs.get(environment))

        if not os.path.isdir(FULL_DIR):
            os.mkdir(FULL_DIR)

        return FULL_DIR

DOWNLOAD_CACHE:  DockerDownloadCache = None 


def download_package_and_create_moduleinfo(
    project: Distribution, 
    environment: lambda_python_environment, 
    module_name: str,
    downloads_directory: str
) -> ModulePackagingInfo:
    """Download a project in a platform compatible way to extract a particular top level module info from the project. 
    
    Note that this function implements a cache so that it only downloads the project the first time it ever is called 
    for the pair (project_name, environment). This means that most calls to this function will not have to actually download the project.

    Args:
        project (Distribution): The distribution object that contains the metadata for the package
        environment (lambda_python_environments): Deployment environment the project needs to support
        module_name (str): The top level module from this project that we want
        base_archive_directory (str): Path to Cache
    Returns:
        info (ModulePackagingInfo): Object for the information on packaging this module
    """
    global DOWNLOAD_CACHE

    DOWNLOAD_CACHE = DockerDownloadCache(downloads_directory)

    
    package_information = _download_package(project, environment)

    potential_modules = [x for x in package_information if x.module_name == module_name]

    if not len(potential_modules) == 1:
        raise Exception

    final_module = potential_modules[0]

    return final_module


def _download_package(
    project: Distribution, environment: lambda_python_environment
) -> List[ModulePackagingInfo]:
    """
    Perform the actual downloading of the package and then parse out the needed information about the top level modules made available
    from the project. Uses the cache to make sure that way we only download the project when actually needed. Also reuses the same container
    when downloading packages so that it uses pip's cache to not redownload the same package.

    Args:
        project (Distribution): The distribution object that contains the metadata for the package
        environment (lambda_python_environments): Deployment environment the project needs to support

    Returns:
        info (List[ModulePackagingInfo]): ModulePackagingInfo for all the top level modules in the project

    """
    global has_run_container
    global build_container

    cache_item = DOWNLOAD_CACHE.find_item(environment, project.project_name)
    if cache_item:
        log.debug("Hit Cache for Download Pkg (%s, %s)", environment, project.project_name)
        return cache_item

    packaging_dir = DOWNLOAD_CACHE.get_packaging_dir(environment)

    
    client = docker.from_env()

    if not environment in CONTAINER_NAMES:
        raise Exception(f"No available Images for building projects on environment {environment}")

    image_name = CONTAINER_NAMES.get(environment)

    print(f"PULLING DOCKER IMAGE {image_name}")

    try:
        client.images.pull(image_name)
    except Exception as e:
        print(e)
        raise Exception(f"Could Not Pull Docker Images {image_name}")
        
    print(f"PULLED IMAGE")

    try:
        if not has_run_container:
            build_container = client.containers.run(
                image_name,
                entrypoint="/var/lang/bin/pip",
                command=f"install {project.project_name}=={project.version} --target /tmp",
                volumes=[f"{packaging_dir}:/tmp"],
                detach=True,
            )

            has_run_container = True

        else:
            build_container.restart()

            build_container.exec_run(
                cmd=f"/var/lang/bin/pip install {project.project_name}=={project.version} --target /tmp",
                detach=True,
            )

        for x in build_container.logs(stream=True):
            msg = x.decode("ascii")
            print(f"Container Output -> {msg}")

    except Exception as e:
        print(e)
        raise Exception(f"Could Install {project.project_name} ({project.version}) using Image {image_name}")

    # Create the actual packaging information and store it in cache via this function
    info = _create_package_info(project.project_name, environment)

    return info


def _create_package_info(
    project_name: str, environment: lambda_python_environment
) -> List[ModulePackagingInfo]:
    """Creates a list of ModulePackagingInfo objects that represent the top level modules made available from this
    package. 
    
    It uses the information from the 'dist-info' that was downloaded for the projects by PIP. This function
    recursively calls itself to compute the information for dependant projects that were downloaded.

    Arg:
        project_name (str): Name of the project to create the information for
        environment (lambda_python_environments): Deployment environment the project needs to support

    Returns:
        info (List[ModulePackagingInfo]): ModulePackagingInfo objects for each of the top level modules in this project
    """

    # We check and add to the cache at this layer because we recursively call this function to compute the
    # information about dependencies of a project. Since projects can share dependencies it saves time from recomputing
    # this info
    cache_item = DOWNLOAD_CACHE.find_item(environment, project_name)
    if cache_item:
        log.debug("Hit Cache for Download Pkg (%s, %s)", environment, project_name)
        return cache_item

    packaging_dir = DOWNLOAD_CACHE.get_packaging_dir(environment)

    dist_info_dir = None

    for _, dir_names, _ in os.walk(packaging_dir):
        # We need to look through the packaging dir to find the dist-info folder for the project.
        # Note the dist-info folder is <project_name>-<version>.dist-info
        # https://www.python.org/dev/peps/pep-0376/#one-dist-info-directory-per-installed-distribution
        regex_dist_info = "(.*).dist-info"

        for dir_name in dir_names:
            m = re.match(regex_dist_info, dir_name)
            if not m:
                continue

            # [<project_name>-<version>, dist-info]
            dir_name_split = m.groups()

            # project_name
            split_name_version = dir_name_split[0].split("-")

            name = split_name_version[0]
            version = split_name_version[1]

            # Note that if a project contains '-' they are converted to '_' so that the above regex/string parsing works, so convert any '-'
            # into '_' when looking for the correct directory
            if name == project_name.replace("-", "_"):
                dist_info_dir = os.path.join(
                    packaging_dir, f"{name}-{version}.dist-info"
                )
                log.debug("Found dist info for (%s, %s) at %s", environment, project_name, dist_info_dir)
                break

        break

    if not dist_info_dir:
        raise Exception(f"Could not find dist info for {project_name} -> {dist_info_dir}")

    if not os.path.isdir(os.path.join(packaging_dir, dist_info_dir)):
        raise Exception(f"COULD NOT FIND {os.path.join(packaging_dir, dist_info_dir)}")

    # If no top level file is found then assume the only top level module is the same as the project name
    if not os.path.isfile(os.path.join(packaging_dir, dist_info_dir, "top_level.txt")):
        top_level_module_names = [project_name]

    else:
        with open(os.path.join(packaging_dir, dist_info_dir, "top_level.txt")) as fh:
            top_level_module_names = [x.strip() for x in fh.readlines()]

        log.debug("top level modules for (%s, %s) are %s", environment, project_name, top_level_module_names)

    tmp_flat_requirements: List[ModulePackagingInfo] = []
    tmp_tree_requirements: List[ModulePackagingInfo] = []
    rv = []

    if not os.path.isfile(os.path.join(packaging_dir, dist_info_dir, "METADATA")):
        # If not metadata file is found then assume no dependencies
        log.debug("COULD NOT FIND %s", os.path.join(packaging_dir, dist_info_dir, 'METADATA'))

    else:
        required_packages = set()
        current_package_version = ""
        with open(os.path.join(packaging_dir, dist_info_dir, "METADATA")) as fh:
            lines = fh.readlines()

            for line in lines:

                if not line:
                    break

                if line.split(":")[0] == "Version":
                    # https://www.python.org/dev/peps/pep-0345/#version
                    # ex:
                    # version: 1.0.2
                    current_package_version = line.split(":")[1].strip()

                if line.split(":")[0] == "Requires-Dist":
                    # https://www.python.org/dev/peps/pep-0345/#requires-dist-multiple-use
                    # ex:
                    # Requires-Dist: pytz (>=2017.3)
                    stripped_information = line.split(":")[1].strip()


                    requirement_project_name = parse_requirement_line(
                        stripped_information
                    )

                    if requirement_project_name:
                        log.debug("Pkg %s requires pkg %s", project_name, requirement_project_name)
                        required_packages.add(requirement_project_name)

        for required_package in required_packages:
            # Recursively find the requirements to each needed project 
            dependent_pkg_infos = _create_package_info(required_package, environment)
            for dependent_pkg_info in dependent_pkg_infos:
                # For the flat data structure add both the dependency and the dependencies dependencies 
                tmp_flat_requirements.extend(dependent_pkg_info.flat)
                tmp_flat_requirements.append(dependent_pkg_info)

                tmp_tree_requirements.append(dependent_pkg_info)

    for top_level_module_name in top_level_module_names:
        # Create module packaging info objects for each of the top level modules of the pkg

        # The package could be either a folder (normal case) or a single python file (ex: 'six' package)
        # If it can not be found as either than there is an issue
        potential_dir = os.path.join(packaging_dir, top_level_module_name)
        potential_file = os.path.join(packaging_dir, top_level_module_name + ".py")

        if os.path.isdir(potential_dir):
            tmp_fp = potential_dir

        elif os.path.isfile(potential_file):
            tmp_fp = potential_file

        else:
            # just continue cause things like numpy have __dummy__ in their top level pkg names but dont provide it
            continue

        info = ModulePackagingInfo(
            **{
                "module_name": top_level_module_name,
                "type": PackageTypes.PIP,
                "version_id": current_package_version,
                "arch": environment_to_architecture_suffix.get(environment),
                "fp": tmp_fp,
                "flat": tmp_flat_requirements,
                "tree": tmp_tree_requirements,
            }
        )

        rv.append(info)

    # Add the information to the cache for this function
    DOWNLOAD_CACHE.add_item(environment, project_name, [x.dict() for x in rv])

    return rv
