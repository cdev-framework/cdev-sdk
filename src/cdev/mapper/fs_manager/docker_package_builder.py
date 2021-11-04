import docker
from pkg_resources import EntryPoint
from cdev.settings import SETTINGS as CDEV_SETTINGS
import os
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


def download_package(pkg: Distribution, pkg_name: str, unmodified_pkg_name: str):
    print(f"DOWNLOADING {pkg} FROM DOCKER")
    client =  docker.from_env()

    client.images.pull("public.ecr.aws/lambda/python:3.8-arm64")
    
    print(f"PULLED IMAGE")
    print(f"RUNNING AS {os.getuid()}")

    container = client.containers.run("public.ecr.aws/lambda/python:3.8-arm64",
                        entrypoint="/var/lang/bin/pip", 
                        command=f"install {pkg.project_name}=={pkg.version} --target /tmp --no-user",
                        volumes=[f'{PACKAGING_DIR}:/tmp'],
                        detach=True,
                        user=os.getuid()
                    )


    for x in container.logs(stream=True):
        print("------")
        msg = x.decode('ascii')
        print(msg)
        if 'Downloading' in msg:

            try:
                package_name, version = tuple(msg.split(" ")[1].split("-")[:2])
                print(f"DOWNLOADED -> {package_name}; {version}")
            except Exception:
                continue

            
            

    rv = PackageInfo(
            pkg_name = unmodified_pkg_name,
            type = PackageTypes.PIP ,
            version_id = pkg.version,
            fp = os.path.join(PACKAGING_DIR, pkg_name)
        )



    return rv

    

    
