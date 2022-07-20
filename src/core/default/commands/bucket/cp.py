"""Command for uploading objects to a Bucket

"""
from argparse import ArgumentParser
import boto3
import os
import mimetypes

from core.constructs.commands import BaseCommand

from core.default.commands import utils as command_utils

from . import utils as bucket_utils

RUUID = "cdev::simple::bucket"


class cp(BaseCommand):
    help = """
    Command to mirror s3 `cp` command.
    """

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "source",
            type=str,
            help="The source of the file. Must either be a local path or bucket location (bucket://<component>.<name>/<path>)",
        )
        parser.add_argument(
            "destination",
            type=str,
            help="The destination of the file. Must either be a local path or bucket location (bucket://<component>.<name>/<path>)",
        )

        parser.add_argument(
            "--recursive",
            action="store_true",
            help="The destination of the file. Must either be a local path or bucket location (bucket://<component>.<name>/<path>)",
        )

    def command(self, *args, **kwargs) -> None:

        source_raw = kwargs.get("source")
        destination_raw = kwargs.get("destination")

        is_recursive = kwargs.get("recursive")

        if bucket_utils.is_valid_remote(source_raw):
            is_source_remote = True
            source = bucket_utils.parse_remote_location(source_raw)

        elif os.path.isfile(source_raw):
            is_source_remote = False
            source = source_raw

        elif os.path.isdir(source_raw) and is_recursive:
            is_source_remote = False
            source = source_raw

        else:
            raise Exception(
                f"Source {source_raw} is neither a valid location on the file system or a valid remote location"
            )

        if bucket_utils.is_valid_remote(destination_raw):
            is_destination_remote = True
            destination = bucket_utils.parse_remote_location(destination_raw)

        elif os.path.isdir(destination_raw):
            is_destination_remote = False
            destination = destination_raw

        elif os.path.isdir(os.path.dirname(destination_raw)):
            is_destination_remote = False
            destination = destination_raw

        else:
            raise Exception(
                f"Destination {destination_raw} is neither a valid location on the file system or a valid remote location"
            )

        if not is_destination_remote and not is_source_remote:
            raise Exception(
                f"Both destination ({destination}) and source ({source}) are file system locations"
            )

        s3 = boto3.resource("s3")

        if is_destination_remote and not is_source_remote:
            # Remote destination and local file system.
            # Copying up
            cloud_output = command_utils.get_cloud_output_from_cdev_name(
                destination.component_name, RUUID, destination.cdev_bucket_name
            )
            bucket_name = cloud_output.get("bucket_name")

            bucket = s3.Bucket(bucket_name)

            if destination.path:
                key_name = destination.path
            else:
                key_name = source

            mimetype, _ = mimetypes.guess_type(source)
            if mimetype is None:
                raise Exception("Failed to guess mimetype")

            self.output.print(f"Upload {source_raw} ->  {destination_raw}")
            bucket.upload_file(source, key_name, ExtraArgs={"ContentType": mimetype})

        if not is_destination_remote and is_source_remote:
            # Local destination and remote source.
            # Pulling down

            cloud_output = command_utils.get_cloud_output_from_cdev_name(
                source.component_name, RUUID, source.cdev_bucket_name
            )
            bucket_name = cloud_output.get("bucket_name")

            bucket = s3.Bucket(bucket_name)

            self.output.print(f"Download {source_raw} -> {destination_raw} ")
            bucket.download_file(source.path, destination)

        if is_destination_remote and is_source_remote:
            # Local destination and remote source.
            # Pulling down

            source_cloud_output = command_utils.get_cloud_output_from_cdev_name(
                source.component_name, RUUID, source.cdev_bucket_name
            )
            source_bucket_name = source_cloud_output.get("bucket_name")
            destination_cloud_output = command_utils.get_cloud_output_from_cdev_name(
                destination.component_name, RUUID, destination.cdev_bucket_name
            )
            destination_bucket_name = destination_cloud_output.get("bucket_name")
            destination_bucket = s3.Bucket(destination_bucket_name)

            destination_key = destination.path if destination.path else source.path

            self.output.print(f"Copy {source_raw} -> {destination_raw}")
            destination_bucket.copy(
                {"Bucket": source_bucket_name, "Key": source.path}, destination_key
            )
