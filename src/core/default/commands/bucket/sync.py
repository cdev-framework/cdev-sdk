
"""Command for syncing a set of resources to a static site
"""
from argparse import ArgumentParser
import boto3
import os
import mimetypes

from core.constructs.commands import BaseCommand, OutputWrapper
from core.default.resources.simple.object_store import Bucket, bucket_model
from core.utils.paths import get_full_path_from_workspace_base

from . import utils


class sync_files(BaseCommand):
    help = """
    Command to sync a folder of content to a bucket
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "resource_name", type=str, help="The bucket resource you want to sync."
        )
        parser.add_argument(
            "--dir",
            type=str,
            help="content folder to sync to the resource.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear the existing content of the bucket before syncing the new data.",
        )

    def command(self, *args, **kwargs):
        full_resource_name: str = kwargs.get("resource_name")
        component_name = full_resource_name.split('.')[0]
        bucket_cdev_name = full_resource_name.split('.')[1]
        content_directory = kwargs.get("dir")
        clear_bucket = kwargs.get("clear")

        cloud_output = utils.get_cloud_output_from_cdev_name(component_name, bucket_cdev_name)

        final_dir = get_full_path_from_workspace_base(content_directory)

        bucket_name = cloud_output.get("bucket_name")
        

        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)

        if clear_bucket:
            bucket.object_versions.delete()


        for subdir, dirs, files in os.walk(final_dir):
            for file in files:
                full_path = os.path.join(subdir, file)

                key_name = os.path.relpath(full_path, final_dir)

                mimetype, _ = mimetypes.guess_type(full_path)
                if mimetype is None:
                    raise Exception("Failed to guess mimetype")
                self.stdout.write(f"Uploading file -> {full_path}")
                bucket.upload_file(
                    full_path, key_name, ExtraArgs={"ContentType": mimetype}
                )
