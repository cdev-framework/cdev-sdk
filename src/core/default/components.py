from core.utils.fs_manager import finder


from core.constructs.components import ComponentModel, Component
from core.utils import hasher


class Cdev_FileSystem_Component(Component):
    """
    A simple implementation of a Cdev Component that uses a folder on the file system to render the desired resources.
    This component uses provided libraries in Cdev to generate resources. Using this component, you can create serverless
    functions using the provided Cdev annotations that also provides functionality to parse the desired folder out of the
    file to make it more efficient.
    """

    def __init__(self, fp, name):
        super().__init__(name)
        self.fp = fp

    def render(self) -> ComponentModel:
        """Render this component based on the information in the files at the provided folder path

        Returns:
            ComponentModel
        """
        resources_sorted, references_sorted = finder.parse_folder(self.fp)
        total_component_hash = hasher.hash_list(
            [x.hash for x in resources_sorted] + [x.hash for x in references_sorted]
        )

        rv = ComponentModel(
            **{
                "resources": list(resources_sorted),
                "hash": total_component_hash,
                "name": self.get_name(),
            }
        )

        return rv
