import site
import boto3
import json
from typing import Any, Dict, List
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.default.resources.simple import static_site
from core.constructs.output_manager import OutputTask
from core.utils import hasher


from .. import aws_client


def _create_simple_static_site(
    transaction_token: str, 
    namespace_token: str, 
    resource:  static_site.simple_static_site_model,
    output_task: OutputTask
) -> Dict:

    
    full_namespace_suffix = hasher.hash_list([namespace_token, str(uuid4())])

    site_name = f"cdev-staticsite-{full_namespace_suffix}" 

    output_task.update(comment=f'Creating Bucket')
    aws_client.run_client_function(
        "s3", "create_bucket", {"Bucket": site_name, "ACL": "public-read"}
    )
   
    output_task.update(comment=f'Add read object policy')
    aws_client.run_client_function(
        "s3",
        "put_bucket_policy",
        {
            "Bucket": site_name,
            "Policy": json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "PublicReadGetObject",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": f"arn:aws:s3:::{site_name}/*",
                        }
                    ],
                }
            ),
        },
    )

    output_task.update(comment=f'Set Website Configuration')
    aws_client.run_client_function(
        "s3",
        "put_bucket_website",
        {
            "Bucket": site_name,
            "WebsiteConfiguration": {
                "ErrorDocument": {"Key": resource.error_document},
                "IndexDocument": {"Suffix": resource.index_document},
            },
        },
    )


    output_info = {
        "site_name": site_name,
        "bucket_name": site_name,
        "cloud_id": f"arn:aws:s3:::{site_name}",
        "site_url": f"http://{site_name}.s3-website-us-east-1.amazonaws.com",
        "arn": f"arn:aws:s3:::{site_name}",
        "cdev_name": resource.name,
    }

   
    #if resource.sync_folder:
    #    output_task.update(comment=f'Sync Files')
    #    file_syncer = sync_files()
    #    file_syncer.command(
    #        **{"resource_name": resource.name, "dir": resource.content_folder}
    #    )


    return output_info


def _update_simple_static_site(
    transaction_token: str, 
    namespace_token: str,
    previous_resource: static_site.simple_static_site_model,
    new_resource: static_site.simple_static_site_model,
    previous_output: Dict,
    output_task: OutputTask
) -> bool:

    site_name = previous_output.get('site_name')

    if not previous_resource.index_document == new_resource.index_document:
        aws_client.run_client_function(
            "s3",
            "put_bucket_website",
            {
                "Bucket": site_name,
                "WebsiteConfiguration": {
                    "ErrorDocument": {"Key": new_resource.error_document},
                    "IndexDocument": {"Suffix": new_resource.index_document},
                },
            },
        )


    if not previous_resource.error_document == new_resource.error_document:
        aws_client.run_client_function(
            "s3",
            "put_bucket_website",
            {
                "Bucket": site_name,
                "WebsiteConfiguration": {
                    "ErrorDocument": {"Key": new_resource.error_document},
                    "IndexDocument": {"Suffix": new_resource.index_document},
                },
            },
        )


    if not previous_resource.sync_folder == new_resource.sync_folder:
        # If there has been a change in sync from false to true then sync the new directory
        #if new_resource.sync_folder:
        #    output_task.update(comment=f'Syncing Files')
        #    
        #    file_syncer = sync_files()
        #    file_syncer.command(
        #        **{
        #            "resource_name": new_resource.name,
        #            "dir": new_resource.content_folder,
        #        }
        #    )
            
        #else:
        #    output_task.update(comment=f'Disbled Sync Files')
        pass


    #elif not previous_resource.content_folder == new_resource.content_folder:
    #    output_task.update(comment=f'Sync Files')
#
    #    # If there was not change to sync but there is a change to the content folder. Clear the bucket and sync new folder
    #    s3 = boto3.resource("s3")
    #    bucket = s3.Bucket(site_name)
    #    bucket.object_versions.delete()
    #   
    #    file_syncer = sync_files()
    #    file_syncer.command(
    #        **{"resource_name": new_resource.name, "dir": new_resource.content_folder}
    #    )
    #    

    # No changes affect the actual cloud output
    return previous_output

def _remove_simple_static_site(
    transaction_token: str, 
    previous_output: Dict, 
    output_task: OutputTask
):

    site_name = previous_output.get('site_name')



    s3 = boto3.resource("s3")
    bucket = s3.Bucket(site_name)
    output_task.update(comment='Deleting all items in the bucket')
    bucket.object_versions.delete()

    output_task.update(comment='Deleting bucket')
    aws_client.run_client_function(
        "s3", "delete_bucket", {"Bucket": site_name}
    )



def handle_simple_static_site_deployment(
        transaction_token: str, 
        namespace_token: str, 
        resource_diff: Resource_Difference, 
        previous_output: Dict[str, Any],
        output_task: OutputTask
    ) -> Dict:
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        return _create_simple_static_site(
            transaction_token,
            namespace_token,
            resource_diff.new_resource,
            output_task
        )
        
    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
        return _update_simple_static_site(
            transaction_token,
            namespace_token,
            static_site.simple_static_site_model(**resource_diff.previous_resource.dict()),
            resource_diff.new_resource,
            previous_output,
            output_task
        )

    elif resource_diff.action_type == Resource_Change_Type.DELETE:
        _remove_simple_static_site(
            transaction_token,
            previous_output,
            output_task
        )

        return {}
