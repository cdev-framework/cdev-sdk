import os
import inspect
import sys

# Keep cache of already seen package names
PACKAGE_CACHE = {}

def create_package_info(pkg_name):
    print(pkg_name)
    if not pkg_name in sys.modules:
        print(f"BAD PKG NAME -> {pkg_name}")
        #print(sys.modules)

    else:
        m = sys.modules.get(pkg_name)
        
