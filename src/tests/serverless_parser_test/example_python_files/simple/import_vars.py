import os
from sys import path as p


def somehandler(event, context):
    print(os.path.join("."))
    print(p)
    return True
