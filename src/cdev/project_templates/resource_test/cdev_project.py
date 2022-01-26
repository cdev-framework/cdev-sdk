# Generated as part of Resource Test project template 

from cdev.default.cloudmapper import DefaultMapper
from cdev.default.components import Cdev_FileSystem_Component

from cdev import Project as cdev_project

myProject = cdev_project.instance()


myProject.add_mapper(
    DefaultMapper()
)


myProject.add_component(
    Cdev_FileSystem_Component("src", "hello_world_comp")
)





