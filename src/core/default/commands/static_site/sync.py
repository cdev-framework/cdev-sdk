"""Command for syncing a set of resources to a static site
"""
from argparse import ArgumentParser
import boto3
import os
import mimetypes

from pydantic import FilePath

from core.constructs.commands import BaseCommand
from core.default.resources.simple.static_site import (
    simple_static_site_model,
)
from core.utils.paths import get_full_path_from_workspace_base
from core.default.commands import utils as command_utils

from core.default.commands.static_site.watcher import StaticSiteWatcher


RUUID = "cdev::simple::staticsite"


class sync_files(BaseCommand):

    _resource_name: str = None

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
        parser.add_argument(
            "--keep-in-sync",
            action="store_true",
            help="Watch for files that get modified and keep them in sync with the bucket",
        )
        parser.add_argument(
            "--no-default",
            action="store_true",
            help="By default we ignore certain files and watch for some others. If you want complete control on what is considered a change, turn this on and set your custom filters using --watch and --ignore",
        )
        parser.add_argument(
            "--watch",
            help="Watch any file that matches the following pattern [*.html, *.js, *.jpg, *.png]",
        )
        parser.add_argument(
            "--ignore",
            help="Do not watch for any file that matches the following pattern [.cdev/**, __pycache__/*, *.py]",
        )

    def command(self, *args, **kwargs) -> None:

        self._extract_arguments(*args, **kwargs)
        if kwargs.get("keep_in_sync"):
            self._watch_filesystem()
        else:
            self._perform_deployment(kwargs.get("resource_name"))

    def _extract_arguments(self, *args, **kwargs) -> None:
        self._resource_name = kwargs["resource_name"]
        self._override_directory = kwargs.get("dir")
        self._clear_bucket_first = kwargs.get("clear")
        self._preserve_html = kwargs.get("preserve_html")
        self._ignore_files = kwargs.get("ignore")
        self._watch_files = kwargs.get("watch")
        self._no_default = kwargs.get("no-default")
        self._no_prompt = kwargs.get("disable-prompt")

    def _perform_deployment(self, resource_name: str) -> None:
        (
            component_name,
            static_site_name,
        ) = command_utils.get_component_and_resource_from_qualified_name(resource_name)

        resource: simple_static_site_model = command_utils.get_resource_from_cdev_name(
            component_name, RUUID, static_site_name
        )
        cloud_output = command_utils.get_cloud_output_from_cdev_name(
            component_name, RUUID, static_site_name
        )

        index_document = resource.index_document
        error_document = resource.error_document
        final_dir = self._get_final_directory(resource)

        s3 = boto3.resource("s3")

        # bucket_name isn't optional
        bucket_name = cloud_output["bucket_name"]
        bucket = s3.Bucket(bucket_name)

        if self._clear_bucket_first:
            bucket.object_versions.delete()

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

                elif (not self._preserve_html) and file.split(".")[1] == "html":
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

    def _watch_filesystem(self) -> None:
        """
        Watch for filesystem changes
        """
        (
            component_name,
            static_site_name,
        ) = self.get_component_and_resource_from_qualified_name(self._resource_name)

        resource: simple_static_site_model = command_utils.get_resource_from_cdev_name(
            component_name, RUUID, static_site_name
        )
        final_dir = self._get_final_directory(resource)

        try:
            static_site_watcher = StaticSiteWatcher(
                final_dir,
                deployment_function=self._perform_deployment,
                no_prompt=self._no_prompt,
                no_default=self._no_default,
                patterns_to_watch=self._watch_files,
                patterns_to_ignore=self._ignore_files,
                output=self.output,
            )
            static_site_watcher.watch()
        except Exception as e:
            print(e)
            return

    def _get_final_directory(self, resource: simple_static_site_model) -> FilePath:
        if not self._override_directory:
            final_dir = get_full_path_from_workspace_base(resource.content_folder)
        else:
            final_dir = get_full_path_from_workspace_base(self._override_directory)
        return final_dir
