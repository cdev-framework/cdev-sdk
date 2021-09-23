from typing import Any, Callable, Dict
from cdev.models import CloudState
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
        pass
        #cloud_mapping.state[identifier].deployed_resources.remove(old_resource)
    except Exception as e:
        print(e)
        return False

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True


def get_output_value_by_hash(identifier: str, key: str, transformer: Callable[[Any], Any]=None) -> Any:
    cloud_mapping =  backend_utils.load_cloud_mapping()

    if not identifier in cloud_mapping.state:
        # TODO throw error
        return None

    if not key in cloud_mapping.state.get(identifier).output:
        # TODO throw error
        return None

    original_data = cloud_mapping.state.get(identifier).output.get(key)

    if transformer:
        print(f"original: {original_data}; transformed {transformer(original_data)}")
        return transformer(original_data)

    return original_data


def get_output_value_by_name(resource_type: str, name: str, key: str ,transformer: Callable[[Any], Any]=None) -> Any:
    cloud_mapping =  backend_utils.load_cloud_mapping()

    for resource_id in cloud_mapping.state:
        if cloud_mapping.state.get(resource_id).output.get("cdev_name") == name and cloud_mapping.state.get(resource_id).output.get("ruuid") == resource_type:
            cloud_output = cloud_mapping.state.get(resource_id).output

            if key not in cloud_output:
                raise Exception
            else:
                return cloud_output.get(key)

    raise Exception

def get_output_by_name(resource_type: str, name: str, transformer: Callable[[Any], Any]=None) -> Dict:
    cloud_mapping =  backend_utils.load_cloud_mapping()

    for resource_id in cloud_mapping.state:
        if cloud_mapping.state.get(resource_id).output.get("cdev_name") == name and cloud_mapping.state.get(resource_id).output.get("ruuid") == resource_type:
            return cloud_mapping.state.get(resource_id).output

    
    raise Exception


def get_output_by_hash(identifier: str) -> Dict:
    cloud_mapping =  backend_utils.load_cloud_mapping()

   
    if not identifier in cloud_mapping.state:
        # TODO throw error
        return None

    return cloud_mapping.state.get(identifier).output



def update_output_value(identifier: str, info: dict) -> bool:
    cloud_mapping =  backend_utils.load_cloud_mapping()

    if not identifier in cloud_mapping.state:
        # TODO throw error
        return None

    cloud_mapping.state[identifier].output.update(info)

    backend_utils.write_cloud_mapping(cloud_mapping)

    return True


def update_output_by_key(identifier: str, key: str, val: Any) -> bool:
    
    full_output = get_output_by_hash(identifier)

    full_output[key] = val

    update_output_value(identifier, full_output)
    
    
    return True
