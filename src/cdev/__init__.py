"""


This tool is designed to improve the developer experience for Serverless development.


[![Demo](https://img.shields.io/badge/demo-holder-blue)](https://img.shields.io/badge/demo-holder-blue)

"""


# from . import commands, cli, settings, utils, constructs, models
#
#
# __all__ = [ "cli", "settings", "commands", "utils", "constructs", "models"]

__pdoc__ = {}
__pdoc__[".venv"] = False


from . import constructs
from core.default.cloudmapper import DefaultMapper
from core.default.components import Cdev_FileSystem_Component

# Ergonomic mapping so that the global project instance is in a more logical place for end developers.
Project = constructs.project.Project
Mapper = DefaultMapper
Component = Cdev_FileSystem_Component
