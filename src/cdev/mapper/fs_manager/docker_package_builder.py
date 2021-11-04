from typing import List
import docker
from pkg_resources import EntryPoint
from cdev.settings import SETTINGS as CDEV_SETTINGS
import os
import json
from pkg_resources import Distribution

from .utils import PackageTypes,PackageInfo

DEPLOYMENT_PLATFORM = CDEV_SETTINGS.get("DEPLOYMENT_PLATFORM")

DEPLOYMENT_PYTHON_VERSION = CDEV_SETTINGS.get("DEPLOYMENT_PYTHON_VERSION")

PACKAGING_DIR = os.path.abspath(os.path.join(CDEV_SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), ".packages"))

CONTAINER_NAMES = {
    "py36": "public.ecr.aws/lambda/python:3.6",
    "py37": "public.ecr.aws/lambda/python:3.7",
    "py38-x86_64": "public.ecr.aws/lambda/python:3.8-x86_64",
    "py38-arm64": "public.ecr.aws/lambda/python:3.8-arm64",
    "py39-x86_64": "public.ecr.aws/lambda/python:3.9-x86_64",
    "py39-arm64": "public.ecr.aws/lambda/python:3.9-arm64",
    "py3-x86_64": "public.ecr.aws/lambda/python:3-x86_64",
    "py3-arm64": "public.ecr.aws/lambda/python:3-arm64",   
}


def docker_available() -> bool:
    return True


CACHE_LOCATION = os.path.join(CDEV_SETTINGS.get("CDEV_INTERMEDIATE_FOLDER_LOCATION"), "dockercache.json")

class DockerDownloadCache:
    """
    Naive cache implentation for know which files have been downloaded.  
    """

    def __init__(self) -> None:

        if not os.path.isfile(CACHE_LOCATION):
            self._cache = {}

        else:

            with open(CACHE_LOCATION) as fh:
                self._cache = json.load(fh)


    def find_item(self, id: str):
        raw_data = self._cache.get(id)
        if raw_data:

            return PackageInfo(**raw_data)
        else:
            None


    def add_item(self, id: str, item: PackageInfo):
        self._cache[id] = item.dict()

        with open(CACHE_LOCATION, "w") as fh:
            json.dump(self._cache, fh, indent=4)


DOWNLOAD_CACHE = DockerDownloadCache()


def download_package(pkg: Distribution, pkg_name: str, unmodified_pkg_name: str):
    cache_item = DOWNLOAD_CACHE.find_item(pkg.project_name)
    if cache_item:
        #print(f"CACHE HIT -> {pkg.project_name} -> {cache_item}")
        return cache_item 
    
    print(f"DOWNLOADING {pkg} FROM DOCKER")
    client =  docker.from_env()

    client.images.pull("public.ecr.aws/lambda/python:3.8-arm64")
    
    print(f"PULLED IMAGE")

    container = client.containers.run("public.ecr.aws/lambda/python:3.8-arm64",
                        entrypoint="/var/lang/bin/pip", 
                        command=f"install {pkg.project_name}=={pkg.version} --target /tmp --no-user",
                        volumes=[f'{PACKAGING_DIR}:/tmp'],
                        detach=True,
                        user=os.getuid()
                    )

    for x in container.logs(stream=True):
        msg = x.decode('ascii')
        print(msg)
    


    info = _create_package_info(pkg.project_name)

    return info

    


def _create_package_info(project_name: str) -> PackageInfo:
    cache_item = DOWNLOAD_CACHE.find_item(project_name)
    if cache_item:
        print(f"CACHE HIT -> {project_name} -> {cache_item}")
        return cache_item 


    for file in os.listdir(PACKAGING_DIR):
        if not file[-9:] == "dist-info":
            continue

        if file.split("-")[0] == project_name.replace("-", "_") and file.split("-")[2] == "info":
            # This is the dist info folder for the pkg
            dist_info_dir = file


    if not os.path.isdir(os.path.join(PACKAGING_DIR,dist_info_dir)):
        raise Exception

    if not os.path.isfile(os.path.join(PACKAGING_DIR,dist_info_dir, "METADATA")):
        raise Exception

    
    # The project name might not always be the same as the top level module name used when importing the project
    if not os.path.isfile(os.path.join(PACKAGING_DIR,dist_info_dir, "top_level.txt")):
        pkg_name = project_name

    else:
        with open(os.path.join(PACKAGING_DIR,dist_info_dir, "top_level.txt")) as fh:
            pkg_name = fh.readline().strip()


    required_packages = []
    current_package_version = ''
    with open(os.path.join(PACKAGING_DIR,dist_info_dir, "METADATA")) as fh:
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
        
    # The package could be either a folder (normal case) or a single python file (ex: 'six' package)
    # If it can not be found as either than there is an issue
    potential_dir = os.path.join(PACKAGING_DIR, pkg_name)
    potential_file = os.path.join(PACKAGING_DIR, pkg_name+".py")
    

    if os.path.isdir(potential_dir):
        tmp_fp = potential_dir

    elif os.path.isfile(potential_file):
        tmp_fp = potential_file

    info = PackageInfo(**{
        "pkg_name": pkg_name,
        "type": PackageTypes.PIP,
        "version_id": current_package_version,
        "fp": tmp_fp
    })

    tmp_flat_requirements = []


    for required_package in required_packages:
        dependent_pkg_info = _create_package_info(required_package)
        tmp_flat_requirements.extend(dependent_pkg_info.flat)
        tmp_flat_requirements.append(dependent_pkg_info)


    info.set_flat(tmp_flat_requirements)    

    DOWNLOAD_CACHE.add_item(project_name, info)

    return info
