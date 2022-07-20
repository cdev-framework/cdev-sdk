import boto3
import json
from typing import Any, Dict
from uuid import uuid4

from core.constructs.resource import Resource_Difference, Resource_Change_Type
from core.default.resources.simple import static_site
from core.constructs.output_manager import OutputTask
from core.utils import hasher


from .. import aws_client


def _create_simple_static_site(
    transaction_token: str,
    namespace_token: str,
    resource: static_site.simple_static_site_model,
    output_task: OutputTask,
) -> Dict:

    full_namespace_suffix = hasher.hash_list([namespace_token, str(uuid4())])

    if not resource.domain_name:
        site_name = f"cdev-staticsite-{full_namespace_suffix}"
    else:
        site_name = resource.domain_name

    output_task.update(comment=f"Creating Bucket")
    aws_client.run_client_function(
        "s3", "create_bucket", {"Bucket": site_name, "ACL": "public-read"}
    )

    output_task.update(comment=f"Add read object policy")
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

    output_task.update(comment=f"Set Website Configuration")
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

    ####################################
    ##### Distribution on CloudFront
    ####################################

    domain_name = f"{site_name}.s3-website-us-east-1.amazonaws.com"

    # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html#managed-cache-policies-list
    # Disabled cache policy
    cache_policy_id = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"

    args = {
        "CallerReference": str(uuid4()),
        "Enabled": True,
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": domain_name,
                    "DomainName": domain_name,
                    "CustomOriginConfig": {
                        "HTTPPort": 80,
                        "HTTPSPort": 443,
                        "OriginProtocolPolicy": "http-only",
                        "OriginSslProtocols": {
                            "Quantity": 3,
                            "Items": ["TLSv1", "TLSv1.1", "TLSv1.2"],
                        },
                        "OriginReadTimeout": 30,
                        "OriginKeepaliveTimeout": 5,
                    },
                }
            ],
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": domain_name,
            "ViewerProtocolPolicy": "redirect-to-https",
            "TrustedSigners": dict(Quantity=0, Enabled=False),
            "AllowedMethods": {
                "Quantity": 2,
                "Items": ["HEAD", "GET"],
                "CachedMethods": {"Quantity": 2, "Items": ["HEAD", "GET"]},
            },
            "CachePolicyId": cache_policy_id,
        },
        "CacheBehaviors": {"Quantity": 0},
        "Comment": "cdev generated",
        "ViewerCertificate": {
            "CloudFrontDefaultCertificate": True,
        },
    }

    if resource.domain_name:
        aliases = {"Aliases": {"Quantity": 1, "Items": [resource.domain_name]}}

        args.update(aliases)

    if resource.ssl_certificate_arn:
        ssl_args = {
            "ViewerCertificate": {
                "CloudFrontDefaultCertificate": False,
                "SSLSupportMethod": "sni-only",
                "MinimumProtocolVersion": "TLSv1.2_2021",
                "ACMCertificateArn": resource.ssl_certificate_arn,
            }
        }

        args.update(ssl_args)

    final_args = {"DistributionConfig": args}

    output_task.update(
        comment=f"[blink]Creating on the Aws Cloudfront CDN. This will take a few minutes[/blink]"
    )

    rv = aws_client.run_client_function("cloudfront", "create_distribution", final_args)

    cloudfront_id = rv.get("Distribution").get("Id")
    cloudfront_arn = rv.get("Distribution").get("ARN")
    cloudfront_domain = rv.get("Distribution").get("DomainName")

    aws_client.monitor_status(
        boto3.client("cloudfront").get_distribution,
        {
            "Id": cloudfront_id,
        },
        "InProgress",
        lambda x: x.get("Distribution").get("Status"),
    )

    output_info = {
        "cloud_id": cloudfront_arn,
        "bucket_name": site_name,
        "cloudfront_id": cloudfront_id,
        "cloudfront_arn": cloudfront_arn,
        "site_url": cloudfront_domain,
    }

    # if resource.sync_folder:
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
    output_task: OutputTask,
) -> Dict:

    if not previous_resource.domain_name == new_resource.domain_name:
        raise Exception(
            "Can not update 'domain_name' via an in place update. You must destroy this version and make a new static site resource."
        )

    if not previous_resource.ssl_certificate_arn == new_resource.ssl_certificate_arn:
        raise Exception(
            "Can not update 'ssl_certificate_arn' via an in place update. You must destroy this version and make a new static site resource."
        )

    bucket_name = previous_output.get("bucket_name")

    if not previous_resource.index_document == new_resource.index_document:
        aws_client.run_client_function(
            "s3",
            "put_bucket_website",
            {
                "Bucket": bucket_name,
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
                "Bucket": bucket_name,
                "WebsiteConfiguration": {
                    "ErrorDocument": {"Key": new_resource.error_document},
                    "IndexDocument": {"Suffix": new_resource.index_document},
                },
            },
        )

    if not previous_resource.sync_folder == new_resource.sync_folder:
        # If there has been a change in sync from false to true then sync the new directory
        # if new_resource.sync_folder:
        #    output_task.update(comment=f'Syncing Files')
        #
        #    file_syncer = sync_files()
        #    file_syncer.command(
        #        **{
        #            "resource_name": new_resource.name,
        #            "dir": new_resource.content_folder,
        #        }
        #    )

        # else:
        #    output_task.update(comment=f'Disbled Sync Files')
        pass

    # elif not previous_resource.content_folder == new_resource.content_folder:
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
    transaction_token: str, previous_output: Dict, output_task: OutputTask
) -> None:
    previous_cloudfront_id = previous_output.get("cloudfront_id")

    all_info = aws_client.run_client_function(
        "cloudfront", "get_distribution", {"Id": previous_cloudfront_id}
    )

    current_distribution_info = all_info.get("Distribution").get("DistributionConfig")
    e_tag = all_info.get("ETag")

    current_distribution_info["Enabled"] = False

    final_args = {
        "DistributionConfig": current_distribution_info,
        "Id": previous_cloudfront_id,
        "IfMatch": e_tag,
    }

    # Disable the distribution
    new_info = aws_client.run_client_function(
        "cloudfront", "update_distribution", final_args
    )
    new_etag = new_info.get("ETag")

    output_task.update(
        comment="[blink]Disabling site on Aws Cloudfront CDN.This will take a few minutes[/blink]"
    )
    aws_client.monitor_status(
        boto3.client("cloudfront").get_distribution,
        {"Id": previous_cloudfront_id},
        "InProgress",
        lambda x: x.get("Distribution").get("Status"),
    )

    output_task.update(comment="Deleting site from Aws Cloudfront CDN")
    aws_client.run_client_function(
        "cloudfront",
        "delete_distribution",
        {"Id": previous_cloudfront_id, "IfMatch": new_etag},
    )

    bucket_name = previous_output.get("bucket_name")

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    output_task.update(comment="Deleting all items in the bucket")
    bucket.object_versions.delete()

    output_task.update(comment="Deleting bucket")
    aws_client.run_client_function("s3", "delete_bucket", {"Bucket": bucket_name})


def handle_simple_static_site_deployment(
    transaction_token: str,
    namespace_token: str,
    resource_diff: Resource_Difference,
    previous_output: Dict[str, Any],
    output_task: OutputTask,
) -> Dict:
    if resource_diff.action_type == Resource_Change_Type.CREATE:
        return _create_simple_static_site(
            transaction_token, namespace_token, resource_diff.new_resource, output_task
        )

    elif resource_diff.action_type == Resource_Change_Type.UPDATE_IDENTITY:
        return _update_simple_static_site(
            transaction_token,
            namespace_token,
            static_site.simple_static_site_model(
                **resource_diff.previous_resource.dict()
            ),
            resource_diff.new_resource,
            previous_output,
            output_task,
        )

    elif resource_diff.action_type == Resource_Change_Type.DELETE:
        _remove_simple_static_site(transaction_token, previous_output, output_task)

        return {}
