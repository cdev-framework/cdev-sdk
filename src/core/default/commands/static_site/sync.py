"""from cdev.management.base import BaseCommand, OutputWrapper
from argparse import ArgumentParser
import boto3
import os
from cdev.backend import cloud_mapper_manager, utils
import mimetypes


RUUID = "cdev::simple::staticsite"


class sync_files(BaseCommand):

    
    ##    Get the logs of a deployed lambda function
    ##

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "resource_name", type=str, help="The function that you want to watch"
        )
        parser.add_argument(
            "--dir",
            type=str,
            help="watch the logs. If this flag is passed, only --start_time flag is read",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="DANGEROUS! Clear the existing content of the bucket before syncing the new data. DANGEROUS!",
        )

    def command(self, *args, **kwargs):
        resource_name = kwargs.get("resource_name")
        override_directory = kwargs.get("dir")
        clear_bucket = kwargs.get("clear")

        if not override_directory:
            final_dir = utils.get_resource(resource_name, RUUID).content_folder

        else:
            final_dir = override_directory

        bucket_name = cloud_mapper_manager.get_output_value_by_name(
            RUUID, resource_name, "bucket_name"
        )
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
"""