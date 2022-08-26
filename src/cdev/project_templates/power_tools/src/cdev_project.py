# Generated as part of Power Tools project template
import os

from cdev import Project, Component, Mapper

myProject = Project.instance()

myProject.add_mapper(Mapper())

myProject.add_component(Component(os.path.join("src", "examples"), "powertools"))
