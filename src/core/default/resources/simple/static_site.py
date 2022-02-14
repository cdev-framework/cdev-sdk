"""Set of constructs for for making a website to serve Static Web Content

"""
from typing import Any

from core.constructs.resource import Resource, ResourceModel, update_hash, ResourceOutputs
from core.constructs.cloud_output import  Cloud_Output_Str
from core.utils import hasher

RUUID = "cdev::simple::staticsite"


class StaticSiteOutput(ResourceOutputs):
    def __init__(self, name: str) -> None:
        super().__init__(name, RUUID)


    @property
    def bucket_name(self) -> Cloud_Output_Str:
        """The name of the underlying S3 Bucket where the content for the site is stored."""
        return Cloud_Output_Str(
            name=self._name,
            ruuid=RUUID,
            key='bucket_name',
            type=self.OUTPUT_TYPE
        )

    @bucket_name.setter
    def bucket_name(self, value: Any):
        raise Exception


    @property
    def site_url(self) -> Cloud_Output_Str:
        """The url of the created site"""
        return Cloud_Output_Str(
            name=self._name,
            ruuid=RUUID,
            key='site_url',
            type=self.OUTPUT_TYPE
        )

    @site_url.setter
    def site_url(self, value: Any):
        raise Exception


###############
##### Static Site
###############
class simple_static_site_model(ResourceModel):
    index_document: str
    """The suffix for documents when request are made for a folder. ex: site.com/dir1/ will look for /dir1/<index_document>"""
    error_document: str
    """The absolute path of document within the site that will be used as a general error page."""
    sync_folder: bool
    """Whether to consider changes in the state of the content folder to trigger a sync of the content folder."""
    content_folder: str
    """The relative path within the Workspace of the folder containting the static content for the site."""


class StaticSite(Resource):
    """A Static Site that can be used to serve static web content. 
    
    """
    
    @update_hash
    def __init__(
        self,
        cdev_name: str,
        index_document: str = "index.html",
        error_document: str = "error.html",
        sync_folder: bool = False,
        content_folder: str = None,
        nonce: str = ""
    ) -> None:
        """Create a static hosted site.

        Arguments:
            cdev_name (str): [description]
            index_document (str): The suffix for documents when request are made for a folder.
            error_document (str): The absolute path of document within the site that will be used as a general error page.
            sync_folder (bool): Whether to consider changes in the state of the content folder to trigger a sync of the content folder.
            content_folder (str): The relative path within the `Workspace` of the folder containting the static content for the site.
            nonce (str): Nonce to make the resource hash unique if there are conflicting resources with same configuration.
        """
        super().__init__(cdev_name, RUUID, nonce)

        self._index_document = index_document
        self._error_document = error_document
        self._sync_folder = sync_folder
        self._content_folder = content_folder

        self.output = StaticSiteOutput(cdev_name)

    @property
    def index_document(self):
        """The suffix for documents when request are made for a folder."""
        return self._index_document

    @index_document.setter
    @update_hash
    def index_document(self, value: str):
        self._index_document = value

    @property
    def error_document(self):
        """The absolute path of document within the site that will be used as a general error page."""
        return self._error_document

    @error_document.setter
    @update_hash
    def error_document(self, value: str):
        self._error_document = value

    @property
    def content_folder(self):
        """The relative path within the `Workspace` of the folder containting the static content for the site."""
        return self._content_folder

    @content_folder.setter
    @update_hash
    def content_folder(self, value: str):
        self._content_folder = value

    @property
    def sync_folder(self):
        """Whether to consider changes in the state of the content folder to trigger a sync of the content folder."""
        return self._sync_folder

    @sync_folder.setter
    @update_hash
    def sync_folder(self, value: bool):
        self._sync_folder = value


    def compute_hash(self):
        # TODO update component to look at the content if the sync folder command is given
        self._hash = hasher.hash_list(
            [
                self.index_document,
                self.error_document,
                self.sync_folder,
                self.content_folder,
                self.nonce
            ]
        )

    def render(self) -> simple_static_site_model:
        if self.sync_folder and not self.content_folder:

            raise Exception(f"If sync_folder is set to 'True' then you must provide a path to the folder.")

        return simple_static_site_model(
            ruuid=self.ruuid,
            name=self.name,
            hash=self.hash,
            index_document=self.index_document,
            error_document=self.error_document,
            sync_folder=self.sync_folder,
            content_folder=self.content_folder,   
        )


