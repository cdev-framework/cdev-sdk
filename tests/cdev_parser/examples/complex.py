# Complex import statements
#  Expected Value
# {
#    "o": {
#        "module": "os",
#        "isroot": True,
#        "aliasFor": None,
#        "isprovided": False,
#    },
#    "functools": {
#        "module": "functools",
#        "isroot": True,
#        "aliasFor": None,
#        "isprovided": False,
#    },
#    "p": {
#    "module": "sys",
#    "isroot": True,
#    "aliasFor": "sys.path",
#    "isprovided": False,
#    },
# }

import os as o
from sys import path as p


def somehandler(event, context):
    print(o.path.join("."))
    print(p)
    return True
