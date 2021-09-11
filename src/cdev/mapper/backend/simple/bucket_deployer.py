from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import logger
from cdev.resources.simple import object_store as simple_object_store
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from ..aws import aws_client as raw_aws_client

log = logger.get_cdev_logger(__name__)
RUUID = "cdev::simple::bucket"

def _create_simple_bucket(identifier: str, resource: simple_object_store.simple_bucket_model) -> bool:
    # TODO create buckets in different region
    raw_aws_client.run_client_function("s3", "create_bucket", {
        "Bucket": resource.bucket_name
    })
    
    
    output_info = {
        "bucket_name": resource.bucket_name,
        "cloud_id": f"arn:aws:s3:::{resource.bucket_name}",
        "arn": f"arn:aws:s3:::{resource.bucket_name}",
        "cdev_name": resource.name,
        "ruuid": RUUID
    }

    cdev_cloud_mapper.add_identifier(identifier),
    cdev_cloud_mapper.update_output_value(identifier, output_info)

    return True

def _update_simple_bucket(previous_resource: simple_object_store.simple_bucket_model, new_resource: simple_object_store.simple_bucket_model) -> bool:
    _remove_simple_bucket(previous_resource.hash, previous_resource)
    _create_simple_bucket(new_resource.hash, new_resource)

    return True


def _remove_simple_bucket(identifier: str, resource: simple_object_store.simple_bucket_model) -> bool:
    raw_aws_client.run_client_function("s3", "delete_bucket", {
        "Bucket": resource.bucket_name
    })

    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")
    return True



def handle_simple_bucket_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_bucket(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            return _update_simple_bucket(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            return _remove_simple_bucket(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")
