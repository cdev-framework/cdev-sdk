
from argparse import ArgumentParser
import boto3
import os
import mimetypes


from core.constructs.commands import BaseCommand, OutputWrapper

from . import utils


class sync_files(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "resource_name", type=str, help="The static site resource you want to sync"
        )
        parser.add_argument(
            "--dir",
            type=str,
            help="override the default content folder of the resource.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear the existing content of the bucket before syncing the new data.",
        )

    def command(self, *args, **kwargs):
        full_resource_name: str = kwargs.get("function_name")
        component_name = full_resource_name.split('.')[0]
        static_site_name = full_resource_name.split('.')[1]
        override_directory = kwargs.get("dir")
        clear_bucket = kwargs.get("clear")

        resource = utils.get_resource_from_cdev_name(component_name, static_site_name)
        cloud_output = utils.get_cloud_output_from_cdev_name(component_name, static_site_name)

        if not override_directory:
            final_dir = resource.get("content_folder")

        else:
            final_dir = override_directory

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

                bucket.upload_file(
                    full_path, key_name, ExtraArgs={"ContentType": mimetype}
                )
