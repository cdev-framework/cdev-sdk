from dataclasses import dataclass
import re


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
        raise Exception(
            "provided name {name} does not match regex for a remote bucket object"
        )

    return remote_location(
        component_name=match.group(1),
        cdev_bucket_name=match.group(2),
        path=match.group(3),
    )
