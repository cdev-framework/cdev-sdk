
"""Command for syncing a set of resources to a static site
"""
from argparse import ArgumentParser
import boto3
import os
import mimetypes

from core.constructs.commands import BaseCommand, OutputWrapper
from core.default.resources.simple.static_site import StaticSite, simple_static_site_model
from core.utils.paths import get_full_path_from_workspace_base

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
        parser.add_argument(
            "--preserve_html",
            action="store_true",
            help="If set, preserve the .html extension for objects.",
        )

    def command(self, *args, **kwargs):
        full_resource_name: str = kwargs.get("resource_name")
        component_name = full_resource_name.split('.')[0]
        static_site_name = full_resource_name.split('.')[1]
        override_directory = kwargs.get("dir")
        clear_bucket = kwargs.get("clear")
        preserve_html = kwargs.get("preserve_html")

        resource: simple_static_site_model = utils.get_resource_from_cdev_name(component_name, static_site_name)
        cloud_output = utils.get_cloud_output_from_cdev_name(component_name, static_site_name)

        if not override_directory:
            t = get_full_path_from_workspace_base(resource.content_folder)
            print(t)
            final_dir = t
            print("p")
        else:
            final_dir = get_full_path_from_workspace_base(override_directory)

        bucket_name = cloud_output.get("bucket_name")
        

        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)

        if clear_bucket:
            bucket.object_versions.delete()

        for subdir, dirs, files in os.walk(final_dir):
            for file in files:
                

                if (not preserve_html) and file.split(".")[1] == 'html':
                    full_path = os.path.join(subdir, file)
                    mimetype = "html"
                    # remove the .html file handle to make the url prettier 
                    key_name = os.path.relpath(full_path, final_dir)[:-5]

                else:
                    full_path = os.path.join(subdir, file)
                    mimetype, _ = mimetypes.guess_type(full_path)
                    key_name = os.path.relpath(full_path, final_dir)

                
                if mimetype is None:
                    raise Exception("Failed to guess mimetype")
                print(f"Uploading file -> {full_path} as {key_name}")
                bucket.upload_file(
                    full_path, key_name, ExtraArgs={"ContentType": mimetype}
                )
