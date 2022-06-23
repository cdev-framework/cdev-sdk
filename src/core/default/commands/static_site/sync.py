"""Command for syncing a set of resources to a static site
"""
from argparse import ArgumentParser
import boto3
import os
import mimetypes

from core.constructs.commands import BaseCommand
from core.default.resources.simple.static_site import (
    simple_static_site_model,
)
from core.utils.paths import get_full_path_from_workspace_base
from core.default.commands import utils as command_utils

RUUID = "cdev::simple::staticsite"


class sync_files(BaseCommand):
    def add_arguments(self, parser: ArgumentParser) -> None:
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
        parser.add_argument(
            "--preserve_html",
            action="store_true",
            help="If set, preserve the .html extension for objects.",
        )

    def command(self, *args, **kwargs) -> None:

        (
            component_name,
            static_site_name,
        ) = command_utils.get_component_and_resource_from_qualified_name(
            kwargs.get("resource_name")
        )

        resource: simple_static_site_model = command_utils.get_resource_from_cdev_name(
            component_name, RUUID, static_site_name
        )
        cloud_output = command_utils.get_cloud_output_from_cdev_name(
            component_name, RUUID, static_site_name
        )

        index_document = resource.index_document
        error_document = resource.error_document

        override_directory = kwargs.get("dir")
        if not override_directory:
            t = get_full_path_from_workspace_base(resource.content_folder)
            final_dir = t
        else:
            final_dir = get_full_path_from_workspace_base(override_directory)

        s3 = boto3.resource("s3")

        bucket_name = cloud_output.get("bucket_name")
        bucket = s3.Bucket(bucket_name)

        clear_bucket = kwargs.get("clear")
        if clear_bucket:
            bucket.object_versions.delete()

        preserve_html = kwargs.get("preserve_html")
        for subdir, dirs, files in os.walk(final_dir):
            for file in files:
                full_path = os.path.join(subdir, file)
                potential_key_name = os.path.relpath(full_path, final_dir)

                if (
                    potential_key_name == index_document
                    or potential_key_name == error_document
                ):
                    # We want to always preserve the index and error documents if they are available
                    mimetype, _ = mimetypes.guess_type(full_path)
                    key_name = potential_key_name

                elif (not preserve_html) and file.split(".")[1] == "html":
                    mimetype = "text/html"
                    # remove the .html file handle to make the url prettier
                    key_name = potential_key_name[:-5]

                else:
                    mimetype, _ = mimetypes.guess_type(full_path)
                    key_name = potential_key_name

                if mimetype is None:
                    mimetype = "text"
                self.output.print(f"{full_path} -> {key_name} ({mimetype})")
                bucket.upload_file(
                    full_path, key_name, ExtraArgs={"ContentType": mimetype}
                )
