
from typing import List

from cdev.core.models import Resource_State


class Project(Resource_State):
    children: List['Environment']


class Environment(Resource_State):
    parent: Project

 
