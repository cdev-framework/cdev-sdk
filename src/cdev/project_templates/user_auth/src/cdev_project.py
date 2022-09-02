# Generated as part of the user auth project template
import os

from cdev import Project, Component, Mapper

myProject = Project.instance()

myProject.add_mapper(Mapper())

myProject.add_component(Component(os.path.join("src", "user_auth"), "user_auth"))
