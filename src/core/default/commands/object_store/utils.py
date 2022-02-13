from dataclasses import dataclass
import re
from tokenize import group

from core.constructs.resource import ResourceModel
from core.constructs.workspace import Workspace

RUUID = "cdev::simple::bucket"

def get_cloud_output_from_cdev_name(component_name: str, cdev_name: str) -> str:
    try:
        ws = Workspace.instance()


        cloud_output = ws.get_backend().get_cloud_output_by_name(
            ws.get_resource_state_uuid(),
            component_name,
            RUUID, 
            cdev_name
        )

        return cloud_output
    except Exception as e:
        print(f"Could not find resource {component_name}:{RUUID}:{cdev_name}")
        print(e)
        return None



def get_resource_from_cdev_name(component_name: str, cdev_name: str) -> ResourceModel:
    try:
        ws = Workspace.instance()


        resource = ws.get_backend().get_resource_by_name(
            ws.get_resource_state_uuid(),
            component_name,
            RUUID, 
            cdev_name
        )

        return resource
    except Exception as e:
        print(f"Could not find resource {component_name}:{RUUID}:{cdev_name}")
        print(e)
        return None


remote_name_regex = "bucket://([a-z,_]+).([a-z,_]+)/?(\S+)?"
compiled_regex = re.compile(remote_name_regex)

@dataclass
class remote_location:
    component_name: str
    cdev_bucket_name: str
    path: str

def is_valid_remote(name: str) -> bool:
    return True if compiled_regex.match(name) else False


def parse_remote_location(name: str) -> remote_location:
    match = compiled_regex.match(name)

    if not match:
        raise Exception("provided name {name} does not match regex for a remote bucket object")

    return remote_location(
        component_name=match.group(1),
        cdev_bucket_name=match.group(2),
        path=match.group(3)
    )



