from enum import Enum
from typing import List
import docker
from cdev.settings import SETTINGS as CDEV_SETTINGS
import os
import json
from pkg_resources import Distribution
import re

from .utils import PackageTypes, ModulePackagingInfo, lambda_python_environments

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
            return [ModulePackagingInfo(**x) for x in raw_data]
        else:
            None


    def add_item(self, environment: lambda_python_environments, id: str, item: ModulePackagingInfo):
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

def download_package(pkg: Distribution, environment: lambda_python_environments, pkg_name: str) -> ModulePackagingInfo:
    package_information = _download_package(pkg, environment)

    potential_modules = [x for x in package_information if x.module_name == pkg_name]


    if not len(potential_modules) == 1:
        return None


    final_module = potential_modules[0]

    return final_module



def _download_package(pkg: Distribution, environment: lambda_python_environments) -> List[ModulePackagingInfo]:
    cache_item = DOWNLOAD_CACHE.find_item(environment, pkg.project_name)
    if cache_item:
        return cache_item 

    packaging_dir = DOWNLOAD_CACHE.get_packaging_dir(environment)
    
    #print(f"DOWNLOADING {pkg} FROM DOCKER")
    client =  docker.from_env()

    client.images.pull("public.ecr.aws/lambda/python:3.8-arm64")
    
    #print(f"PULLED IMAGE")

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

    


def _create_package_info(project_name: str,  environment: lambda_python_environments) -> List[ModulePackagingInfo]:
    """
    Creates a list of ModulePackagingInfo objects that represent the top level modules made available from this 
    package. It uses a cache to make sure the subsequent calls do not have to recompute the dependencies. 
    """

    cache_item = DOWNLOAD_CACHE.find_item(environment, project_name)
    if cache_item:
        print(f"CACHE HIT -> {project_name} -> {cache_item}")
        return cache_item 

    packaging_dir = DOWNLOAD_CACHE.get_packaging_dir(environment)

    dist_info_dir = None
    for _,dir_names,_ in os.walk(packaging_dir):
        regex_dist_info = "(.*).dist-info"
        

        for dir_name in dir_names:
            m = re.match(regex_dist_info, dir_name)
            if not m:
                print(f"No regex match {dir_name} -> {regex_dist_info}")
                continue

            dir_name_split = m.groups()
            print(dir_name_split)
            
            print(f"checking {dir_name_split[0]}")
            split_name_version = dir_name_split[0].split("-") 

            name = split_name_version[0].replace("-", "_")
            version = split_name_version[1]


            if name == project_name.replace("-","_"):
                dist_info_dir = os.path.join(packaging_dir, f"{name}-{version}.dist-info")
                break
        break 

    if not dist_info_dir:
        print(f"Could not find dist info for {project_name}")
        raise Exception

    if not os.path.isdir(os.path.join(packaging_dir, dist_info_dir)):
        print(f"COULD NOT FIND {os.path.join(packaging_dir, dist_info_dir)}")
        raise Exception

    if not os.path.isfile(os.path.join(packaging_dir, dist_info_dir, "METADATA")):
        print(f"COULD NOT FIND {os.path.join(packaging_dir, dist_info_dir, 'METADATA')}")
        raise Exception

    
    # The project name might not always be the same as the top level module name used when importing the project
    if not os.path.isfile(os.path.join(packaging_dir, dist_info_dir, "top_level.txt")):
        top_level_pkg_names = [project_name]

    else:
        with open(os.path.join(packaging_dir, dist_info_dir, "top_level.txt")) as fh:
            top_level_pkg_names = [x.strip() for x in fh.readlines()]


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
    


    tmp_flat_requirements: List[ModulePackagingInfo] = []
    rv = []


    for required_package in required_packages:

        dependent_pkg_infos = _create_package_info(required_package, environment)
        for dependent_pkg_info in dependent_pkg_infos:
            tmp_flat_requirements.extend(dependent_pkg_info.flat)
            tmp_flat_requirements.append(dependent_pkg_info)
    

    for pkg_name in top_level_pkg_names:
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

        info = ModulePackagingInfo(**{
            "module_name": pkg_name,
            "type": PackageTypes.PIP,
            "version_id": current_package_version,
            "fp": tmp_fp
        })


        info.set_flat(tmp_flat_requirements) 

        rv.append(info)   

    DOWNLOAD_CACHE.add_item(environment, project_name, [x.dict() for x in rv])

    return rv
