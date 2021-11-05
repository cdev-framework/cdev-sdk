from enum import Enum
from typing import List
import docker
from cdev.settings import SETTINGS as CDEV_SETTINGS
import os
import json
from pkg_resources import Distribution

from .utils import PackageTypes,PackageInfo, lambda_python_environments

DEPLOYMENT_PLATFORM = CDEV_SETTINGS.get("DEPLOYMENT_PLATFORM")

DEPLOYMENT_PYTHON_VERSION = CDEV_SETTINGS.get("DEPLOYMENT_PYTHON_VERSION")


def docker_available() -> bool:
    return True


CACHE_LOCATION = os.path.join(CDEV_SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "dockercache.json")

class DockerDownloadCache:
    """
    Naive cache implentation for know which files have been downloaded.  
    """

    def __init__(self) -> None:

        if not os.path.isfile(CACHE_LOCATION):
            self._cache = {
                lambda_python_environments.py36: {},
                lambda_python_environments.py37: {},
                lambda_python_environments.py38_x86_64: {},
                lambda_python_environments.py38_arm64: {},
                lambda_python_environments.py39_x86_64: {},
                lambda_python_environments.py39_arm64: {},
                lambda_python_environments.py3_x86_64: {},
                lambda_python_environments.py3_arm64: {},
            }


        else:
            with open(CACHE_LOCATION) as fh:
                self._cache = json.load(fh)


        self._cache_dirs = {
            lambda_python_environments.py36: "py36",
            lambda_python_environments.py37: "py37",
            lambda_python_environments.py38_x86_64: "py38x8664",
            lambda_python_environments.py38_arm64: "py38arm64",
            lambda_python_environments.py39_x86_64: "py39x8664",
            lambda_python_environments.py39_arm64: "py39arm64",
            lambda_python_environments.py3_x86_64: "py3x8664",
            lambda_python_environments.py3_arm64: "py3arm64",
        }


    def find_item(self, environment: lambda_python_environments, id: str):
        raw_data = self._cache.get(environment).get(id)
        if raw_data:
            return [PackageInfo(**x) for x in raw_data]
        else:
            None


    def add_item(self, environment: lambda_python_environments, id: str, item: PackageInfo):
        self._cache[environment][id] = item

        with open(CACHE_LOCATION, "w") as fh:
            json.dump(self._cache, fh, indent=4)


    def get_packaging_dir(self, environment: lambda_python_environments):
        BASE_PACKAGING_DIR = os.path.abspath(os.path.join(CDEV_SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), ".packages"))

        if not os.path.isdir(BASE_PACKAGING_DIR):
            os.mkdir(BASE_PACKAGING_DIR)


        FULL_DIR = os.path.join(BASE_PACKAGING_DIR, self._cache_dirs.get(environment))

        if not os.path.isdir(FULL_DIR):
            os.mkdir(FULL_DIR)
    
        return FULL_DIR


DOWNLOAD_CACHE = DockerDownloadCache()


def download_package(pkg: Distribution, environment: lambda_python_environments, pkg_name: str, unmodified_pkg_name: str) -> List[PackageInfo]:
    cache_item = DOWNLOAD_CACHE.find_item(environment, pkg.project_name)
    if cache_item:
        #print(f"CACHE HIT -> {pkg.project_name} -> {cache_item}")
        return cache_item 

    packaging_dir = DOWNLOAD_CACHE.get_packaging_dir(environment)
    
    print(f"DOWNLOADING {pkg} FROM DOCKER")
    client =  docker.from_env()

    client.images.pull("public.ecr.aws/lambda/python:3.8-arm64")
    
    print(f"PULLED IMAGE")

    container = client.containers.run("public.ecr.aws/lambda/python:3.8-arm64",
                        entrypoint="/var/lang/bin/pip", 
                        command=f"install {pkg.project_name}=={pkg.version} --target /tmp --no-user",
                        volumes=[f'{packaging_dir}:/tmp'],
                        detach=True,
                        user=os.getuid()
                    )
    
    for x in container.logs(stream=True):
        msg = x.decode('ascii')
        print("Building Package")


    info = _create_package_info(pkg.project_name, environment)

    return info

    


def _create_package_info(project_name: str, environment: lambda_python_environments) -> List[PackageInfo]:
    cache_item = DOWNLOAD_CACHE.find_item(environment, project_name)
    if cache_item:
        print(f"CACHE HIT -> {project_name} -> {cache_item}")
        return cache_item 

    packaging_dir = DOWNLOAD_CACHE.get_packaging_dir(environment)

    for file in os.listdir(packaging_dir):
        if not file[-9:] == "dist-info":
            continue

        if file.split("-")[0] == project_name.replace("-", "_") and file.split("-")[2] == "info":
            # This is the dist info folder for the pkg
            dist_info_dir = file


    if not os.path.isdir(os.path.join(packaging_dir, dist_info_dir)):
        raise Exception

    if not os.path.isfile(os.path.join(packaging_dir, dist_info_dir, "METADATA")):
        raise Exception

    
    # The project name might not always be the same as the top level module name used when importing the project
    if not os.path.isfile(os.path.join(packaging_dir, dist_info_dir, "top_level.txt")):
        pkg_names = [project_name]

    else:
        with open(os.path.join(packaging_dir, dist_info_dir, "top_level.txt")) as fh:
            pkg_names = [x.strip() for x in fh.readlines()]


    required_packages = []
    current_package_version = ''
    with open(os.path.join(packaging_dir, dist_info_dir, "METADATA")) as fh:
        lines = fh.readlines()

        for line in lines:
            if not line:
                break

            if line.split(":")[0] == "Version":
                current_package_version = line.split(":")[1].strip()

            if line.split(":")[0] == "Requires-Dist":
                required_info = line.split(":")[1]

                if len(required_info.split(";")) > 1:
                    # https://packaging.python.org/specifications/core-metadata/#provides-extra-multiple-use
                    # This line has an extra tag and should not be included
                    continue

                required_packages.append(line.split(":")[1].strip().split(" ")[0])
    
    rv = []

    for pkg_name in pkg_names:
        # The package could be either a folder (normal case) or a single python file (ex: 'six' package)
        # If it can not be found as either than there is an issue
        potential_dir = os.path.join(packaging_dir, pkg_name)
        potential_file = os.path.join(packaging_dir, pkg_name+".py")


        if os.path.isdir(potential_dir):
            tmp_fp = potential_dir

        elif os.path.isfile(potential_file):
            tmp_fp = potential_file

        else:
            continue

        info = PackageInfo(**{
            "pkg_name": pkg_name,
            "type": PackageTypes.PIP,
            "version_id": current_package_version,
            "fp": tmp_fp
        })

        tmp_flat_requirements = []

        print(f"{project_name} requires -> {required_packages}")
        for required_package in required_packages:

            dependent_pkg_infos = _create_package_info(required_package, environment)

            for dependent_pkg_info in dependent_pkg_infos:
                tmp_flat_requirements.extend(dependent_pkg_info.flat)
                tmp_flat_requirements.append(dependent_pkg_info)



        info.set_flat(tmp_flat_requirements) 

        rv.append(info)   

    DOWNLOAD_CACHE.add_item(environment, project_name, [x.dict() for x in rv])

    return rv
