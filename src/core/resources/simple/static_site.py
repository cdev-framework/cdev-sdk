from enum import Enum
from typing import Optional

from core.constructs.resource import Resource, ResourceModel, Cloud_Output
from core.utils import hasher


class simple_static_site_model(ResourceModel):
    site_name: str
    """Name of the site this page will be for. The site name must match the final dns domain that will be used if this site will be served with a simple cdn."""
    index_document: str
    """The suffix for documents when request are made for a folder. ex: site.com/dir1/ will look for /dir1/<index_document>"""
    error_document: str
    sync_folder: bool
    content_folder: Optional[str]


class simple_static_site_output(str, Enum):
    cloud_id = "cloud_id"
    bucket_name = "bucket_name"
    site_url = "site_url"


class StaticSite(Resource):
    RUUID = "cdev::simple::staticsite"

    def __init__(
        self,
        cdev_name: str,
        site_name: str = "",
        index_document: str = "index.html",
        error_document: str = "error.html",
        sync_folder: bool = False,
        content_folder: str = None,
    ) -> None:
        """
        Create a static hosted site.

        Args:
            cdev_name (str): Name of the resource
            site_name (str, optional): base name of the bucket in s3.
        """
        super().__init__(cdev_name)

        self.site_name = site_name if site_name else "cdev_staticsite"
        self.index_document = index_document
        self.error_document = error_document
        self.sync_folder = sync_folder
        self.content_folder = content_folder

        if self.sync_folder and not self.content_folder:
            print(
                f"If sync_folder is set to 'True' then you must provide a path to the folder."
            )

            raise Exception

        self.hash = hasher.hash_list(
            [
                self.site_name,
                self.index_document,
                self.error_document,
                self.sync_folder,
                self.content_folder,
            ]
        )

    def render(self) -> simple_static_site_model:
        return simple_static_site_model(
            ruuid=self.RUUID,
            name=self.name,
            hash=self.hash,
            site_name=self.site_name,
            index_document=self.index_document,
            error_document=self.error_document,
            sync_folder=self.sync_folder,
            content_folder=self.content_folder,   
        )

    def from_output(self, key: simple_static_site_output) -> Cloud_Output:
        return super().from_output(key)
