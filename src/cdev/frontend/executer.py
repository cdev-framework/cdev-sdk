import logging.config
import os

from sortedcontainers.sortedlist import SortedList

from cdev.settings import SETTINGS as cdev_settings
from cdev.utils import hasher

from ..constructs import Cdev_Project, Cdev_Component
from ..models import Rendered_State

from ..utils.logger import get_cdev_logger


"""
This file defines the way that a project is parsed and executed to produce the frontend state. 

The Cdev project object is the singleton that represents the information and configuration of the current Cdev Project.

"""

log = get_cdev_logger(__name__)


def execute_frontend() -> Rendered_State:
    """
    This is the function that executes the code to generate a desired state for the project. 

    The order of the execution is:

    - Import the cdev project file
        - This should cause all components to be initialized
    - For each Cdev Component attached to the project 
        - Call the `render` method to get the desired resources and add that to the total state
    - Return a rendered state object
    """

    # TODO throw error
    ALL_COMPONENTS = Cdev_Project.instance().get_components()

    project_components_sorted = SortedList(key=lambda x: x.name)
    log.info({"a" :"b"})
    # Generate the local states
    for component in ALL_COMPONENTS:
        if isinstance(component, Cdev_Component):
            project_components_sorted.add(component.render())
        else:
            print("NOT FILE TYPE")

    project_hash = hasher.hash_list([x.hash for x in project_components_sorted])

    project = Rendered_State(
        **{
            "rendered_components": list(project_components_sorted),
            "hash": project_hash,
        }
    )


    return project


