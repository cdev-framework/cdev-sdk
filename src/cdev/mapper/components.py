
from cdev.utils.exceptions import Cdev_Error, Cdev_Warning
from .fs_manager import finder

from cdev.constructs import Cdev_Component
from cdev.models import Rendered_Component 
from cdev.utils import hasher


class Cdev_FileSystem_Component(Cdev_Component):
    """
        A simple implementation of a Cdev Component that uses a folder on the file system to render the desired resources.
        This component uses provided libraries in Cdev to generate resources. Using this component, you can create serverless
        functions using the provided Cdev annotations that also provides functionality to parse the desired folder out of the 
        file to make it more efficient. 
    """
    def __init__(self, fp, name):
        super().__init__(name)
        self.fp = fp

    def render(self) -> Rendered_Component:
        """Render this component based on the information in the files at the provided folder path"""
        resources_sorted = finder.parse_folder(self.fp, self.get_name())
        total_component_hash =  hasher.hash_list([x.hash for x in resources_sorted])

        rv = Rendered_Component (
            **{
                "rendered_resources": resources_sorted,
                "hash": total_component_hash,
                "name": self.get_name(),
            }
        )
        

        return rv
