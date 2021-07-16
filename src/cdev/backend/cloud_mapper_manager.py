from os import truncate
from cdev.backend.models import CloudState
from . import utils as backend_utils


def add_cloud_resource(identifier: str, new_resource: dict) -> bool:
    """
    This function appends a new object to the identified resource
    """


    cloud_mapping =  backend_utils.load_cloud_mapping()


    if cloud_mapping.state.get(identifier):
        cloud_mapping.state[identifier].deployed_resources.append(new_resource)
    else:
        cloud_mapping.state[identifier] = CloudState(**{
            "deployed_resources": [new_resource],
            "output": {}
        } )

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True


def add_identifier(identifier) -> bool:
    cloud_mapping =  backend_utils.load_cloud_mapping()
    
    if identifier in cloud_mapping.state:
        # TODO throw error
        return False

    cloud_mapping.state[identifier] = CloudState(**{
        "deployed_resources": [],
        "output": {}
    })

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True



def remove_identifier(identifier) -> bool:
    cloud_mapping =  backend_utils.load_cloud_mapping()
    if not identifier in cloud_mapping.state:
        # TODO throw error
        return False

    cloud_mapping.state.pop(identifier)

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True


def reidentify_cloud_resource(old_identifier: str, new_identifier: str):
    cloud_mapping =  backend_utils.load_cloud_mapping()

    if not old_identifier in cloud_mapping.state:
        # TODO throw error
        return False

    cloud_mapping.state[new_identifier] = cloud_mapping.state[old_identifier]
    cloud_mapping.state.pop(old_identifier)

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True


def remove_cloud_resource(identifier: str, old_resource) -> bool: 
    cloud_mapping =  backend_utils.load_cloud_mapping()

    if not identifier in cloud_mapping.state:
        # TODO throw error
        return False

    try:
        
        cloud_mapping.state[identifier].deployed_resources.remove(old_resource)
    except Exception as e:
        print(e)
        return False

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True


def get_output_value(identifier: str, key: str) -> str:
    cloud_mapping =  backend_utils.load_cloud_mapping()

    if not identifier in cloud_mapping.state:
        # TODO throw error
        return None

    if not key in cloud_mapping.state.get(identifier).output:
        # TODO throw error
        return None

    return cloud_mapping.state.get(identifier).output.get(key)


def update_output_value(identifier: str, info: dict) -> bool:
    cloud_mapping =  backend_utils.load_cloud_mapping()

    if not identifier in cloud_mapping.state:
        # TODO throw error
        return None

    cloud_mapping.state[identifier].output.update(info)

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True