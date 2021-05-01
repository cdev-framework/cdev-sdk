import os as o
from sys import path as p


def somehandler(event, context):
    print(o.path.join("."))
    print(p)
    return True
