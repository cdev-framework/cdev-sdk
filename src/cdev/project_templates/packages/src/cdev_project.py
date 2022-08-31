# Generated as part of Packages project template
import os

from cdev import Project, Component, Mapper

myProject = Project.instance()

myProject.add_mapper(Mapper())

myProject.add_component(Component(os.path.join("src", "packages"), "packages_test"))
