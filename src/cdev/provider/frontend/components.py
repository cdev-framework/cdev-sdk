
import hashlib

from ..fs_manager import finder

from cdev.frontend.constructs import Cdev_Component
from cdev.frontend.models import Rendered_Component 


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

    def render(self) -> Rendered_Component :
        """Render this component based on the information in the files at the provided folder path"""
        resources_sorted = finder.parse_folder(self.fp, self.get_name())

        appended_hashes = ":".join([x.hash for x in resources_sorted])

        total_component_str = ":".join(appended_hashes)
        
        total_component_hash = hashlib.md5(total_component_str.encode()).hexdigest()



        rv = Rendered_Component (
            **{
                "rendered_resources": resources_sorted,
                "hash": total_component_hash,
                "name": self.get_name()
            }
        )

        return rv
