from . import utils as backend_utils


def add_cloud_resource(identifier: str, new_resource: dict) -> bool:
    """
    This function appends a new object to the identified resource
    """


    cloud_mapping =  backend_utils.load_cloud_mapping()

    if identifier in cloud_mapping.state:
        # TODO throw error
        return False

    if cloud_mapping.state.get(identifier):
        cloud_mapping.state[identifier].append(new_resource)
    else:
        cloud_mapping.state[identifier] = [new_resource]

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True


def add_indentifier(identifier) -> bool:
    cloud_mapping =  backend_utils.load_cloud_mapping()
    if identifier in cloud_mapping.state:
        # TODO throw error
        return False

    cloud_mapping.state[identifier] = []

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True



def remove_indentifier(identifier) -> bool:
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
        cloud_mapping.state[identifier].remove(old_resource)
    except Exception as e:
        print(e)
        return False

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True
