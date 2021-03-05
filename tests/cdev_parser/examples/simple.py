# Simple test file to see if the parser correctly defines imports
# Dont test line number and col offset
#  Expected Value
# {
#    "os": {
#        "module": "os",
#        "isroot": True,
#        "aliasFor": None,
#        "isprovided": False,
#    },
#    "sys": {
#        "module": "sys",
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
# }

import os
import sys

a = "HELLO"

def somehandler(event, context):
    print(a)
    print(os.path.join("."))
    print(sys.path)
    return True
