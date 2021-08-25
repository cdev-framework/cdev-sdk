import logging.config
import os

from sortedcontainers.sortedlist import SortedList

from cdev.settings import SETTINGS as cdev_settings
from cdev.utils import hasher

from ..constructs import Cdev_Project, Cdev_Component
from ..models import Rendered_State

from ..utils.logger import get_cdev_logger

from ..utils.exceptions import Cdev_Error, end_process



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

    try:
        ALL_COMPONENTS = Cdev_Project.instance().get_components()
        log.info(f"Components in project -> {ALL_COMPONENTS}")

        project_components_sorted = SortedList(key=lambda x: x.name)
        log.debug(f"Sorted Components by name -> {project_components_sorted}")

        # Generate the local states
        for component in ALL_COMPONENTS:
            if isinstance(component, Cdev_Component):
                rendered_state = component.render()
                log.debug(f"component {component} rendered to -> {rendered_state}")
                project_components_sorted.add(rendered_state)
            else:
                raise Cdev_Error(f"{component} is not of type Cdev_Component; Type is {type(Cdev_Component)} ")

        project_hash = hasher.hash_list([x.hash for x in project_components_sorted])
        log.debug(f"New project hash -> {project_hash}")

        project = Rendered_State(
            **{
                "rendered_components": list(project_components_sorted),
                "hash": project_hash,
            }
        )

        return project
    except Cdev_Error as e:
        log.error(e.msg)
        end_process()

    


