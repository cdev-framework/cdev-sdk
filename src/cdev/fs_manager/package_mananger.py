import os
import sys
import pkg_resources

# Keep cache of already seen package names
PACKAGE_CACHE = {}

# There isn't a great runtime way of identifying python standard libraries (non C builtin libraries packaged with python).
# So I scraped the information from the python documentation website using the ./scripts/list-python-builtins
STANDARD_LIBRARY_FILES = ['3_6', "3_7", "3_8"]

# Build a dict of pkg name to pip package obj so you don't have to loop over all the packages when doing a look up
PKG_NAME_TO_PIP_PKG = {}
for f in pkg_resources.working_set:
    PKG_NAME_TO_PIP_PKG[f.key] = f


class PackageTypes:
    BUILTIN = "builtin"
    STANDARDLIB = "standardlib"
    PIP = "pip"
    LOCALPACKAGE = "localpackage"
    AWSINCLUDED = "awsincluded"


def get_package_info(pkg_name):
    info =  create_package_info(pkg_name)

    if info.get("flat"):
        return info.get("flat")

    return set()


def create_package_info(pkg_name):
    # RV :  {
    #   pkg_name: pkg_name,
    #   type: ENUM("builtin", "standardlib", "pip", "localpackage", "awsincluded")
    #   ?Dependencies: SET({<objs>}),
    #   ?AsList: [{objs}],
    #   ?fp: path_to_dir
    # }
    return _recursive_create_package_info(pkg_name)

def _recursive_create_package_info(pkg_name):

    if pkg_name in PACKAGE_CACHE:
        #print(f"CACHE HIT -> {pkg_name}")
        return PACKAGE_CACHE.get(pkg_name)
        

    rv =  {"pkg_name": pkg_name}
    if not pkg_name in sys.modules and not pkg_name in PKG_NAME_TO_PIP_PKG:
        print(f"BAD PKG NAME -> {pkg_name}")
        #print(sys.modules)
        return {}

    else:
        standard_lib_info = _load_standard_library_information("3_6")
        aws_packages = _load_aws_packages("3_6")
        pip_packages = _load_pip_packages()
        m = sys.modules.get(pkg_name)
        

        if pkg_name in standard_lib_info:
            rv["type"] = PackageTypes.STANDARDLIB 

        elif pkg_name in aws_packages:
            rv["type"] = PackageTypes.AWSINCLUDED

        elif pkg_name in pip_packages:
            rv["type"] = PackageTypes.PIP
            rv["fp"] = os.path.join(pip_packages.get(pkg_name).location, pkg_name)

        else:
            if m:
                if not m.__file__:
                    rv["type"] = PackageTypes.BUILTIN
            else:
                rv["type"] = PackageTypes.LOCALPACKAGE

        dependencies = _recursive_check_for_dependencies(rv, [])

        rv["tree"] = dependencies.get("tree")
        rv["flat"] = dependencies.get("flat")

        PACKAGE_CACHE[pkg_name] = rv

        return rv


    
def _recursive_check_for_dependencies(obj, parents):
    if obj.get("type") == PackageTypes.BUILTIN or obj.get("type") == PackageTypes.STANDARDLIB or obj.get("type") == PackageTypes.AWSINCLUDED:
        return obj

    if obj.get("type") == PackageTypes.PIP:
        item = PKG_NAME_TO_PIP_PKG.get(obj.get("pkg_name"))

        rv = {}
        rv['flat'] = set([obj.get('pkg_name')])
        rv['tree'] = []

        for req in item.requires():
            tmp = _recursive_create_package_info(req.key)

            rv["tree"].append(tmp)
            if tmp.get("flat"):
                rv['flat'] = rv["flat"].union(tmp.get("flat"))

        return rv

    return obj
    

        


def _load_standard_library_information(version="3_6"):
    FILE_LOC = os.path.join(os.path.dirname(__file__), "standard_library_names", f"python_{version}")

    if not os.path.isfile(FILE_LOC):
        # TODO throw error
        raise FileNotFoundError
        
    with open(FILE_LOC) as fh:
        return set(fh.read().splitlines())


def _load_aws_packages(version="3_6"):
    return set(["boto3", "botocore"])

def _load_pip_packages():
    return PKG_NAME_TO_PIP_PKG
    
