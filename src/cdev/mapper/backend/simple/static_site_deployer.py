from enum import Enum
from typing import Dict, List

from cdev.models import Resource_State_Difference, Action_Type
from cdev.utils import hasher, logger
from cdev.resources.simple import static_site as simple_static_site
from cdev.resources.simple.commands.static_site.sync import sync_files
from cdev.backend import cloud_mapper_manager as cdev_cloud_mapper
from cdev.output import print_deployment_step
from ..aws import aws_client as raw_aws_client
import json

log = logger.get_cdev_logger(__name__)
RUUID = 'cdev::simple::staticsite'


def _create_simple_static_site(identifier: str, resource: simple_static_site.simple_static_site_model ) -> bool:
    # TODO create buckets in different region
    raw_aws_client.run_client_function("s3", "create_bucket", {
        "Bucket": resource.site_name,
        "ACL": "public-read"
    })
    
    print_deployment_step("CREATE", f"  created underlying bucket {resource.name}")
    raw_aws_client.run_client_function("s3", "put_bucket_policy", {
        "Bucket": resource.site_name,
        "Policy": json.dumps({
            "Version": "2012-10-17",
            "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{resource.site_name}/*"
            }
            ]
        })
    })


    raw_aws_client.run_client_function("s3", "put_bucket_website", {
        'Bucket': resource.site_name,
        'WebsiteConfiguration': {
            "ErrorDocument": {
                "Key": resource.error_document
            }, 
            "IndexDocument": {
                "Suffix": resource.index_document
            }
        }
    })

    print_deployment_step("CREATE", f"  turned bucket into website")
    
    output_info = {
        "bucket_name": resource.site_name,
        "cloud_id": f"arn:aws:s3:::{resource.site_name}",
        "site_url": f"http://{resource.site_name}.s3-website-us-east-1.amazonaws.com",
        "arn": f"arn:aws:s3:::{resource.site_name}",
        "cdev_name": resource.name,
        "ruuid": RUUID
    }

    cdev_cloud_mapper.add_identifier(identifier),
    cdev_cloud_mapper.update_output_value(identifier, output_info)

    if resource.sync_folder:
        print_deployment_step("CREATE", f"  syncing files")
        file_syncer = sync_files()
        file_syncer.command(**{
            "resource_name": resource.name,
            "dir": resource.content_folder
        })
        print_deployment_step("CREATE", f"  synced files")

    return True

def _update_simple_static_site(previous_resource:  simple_static_site.simple_static_site_model, new_resource: simple_static_site.simple_static_site_model) -> bool:
    _remove_simple_static_site(previous_resource.hash, previous_resource)
    _create_simple_static_site(new_resource.hash, new_resource)

    return True


def _remove_simple_static_site(identifier: str, resource: simple_static_site.simple_static_site_model) -> bool:
    raw_aws_client.run_client_function("s3", "delete_bucket", {
        "Bucket": resource.site_name
    })

    print_deployment_step("DELETE", f"Removed bucket {resource.name}")

    cdev_cloud_mapper.remove_cloud_resource(identifier, resource)
    cdev_cloud_mapper.remove_identifier(identifier)
    log.debug(f"Delete information in resource and cloud state")
    return True



def handle_simple_static_site_deployment(resource_diff: Resource_State_Difference) -> bool:
    try:
        if resource_diff.action_type == Action_Type.CREATE:
            return _create_simple_static_site(resource_diff.new_resource.hash, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.UPDATE_IDENTITY:
            return _update_simple_static_site(resource_diff.previous_resource, resource_diff.new_resource)
        elif resource_diff.action_type == Action_Type.DELETE:
            return _remove_simple_static_site(resource_diff.previous_resource.hash, resource_diff.previous_resource)

    except Exception as e:
        print(e)
        raise Exception("COULD NOT DEPLOY")



