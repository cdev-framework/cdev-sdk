import os
from typing import List, Tuple, Set

from .package_generator import DistributionEnvironment


def get_standard_library_modules(version="3_7") -> Set[str]:
    """Get the set of names of standard libraries for a given python version

    Args:
        version (str, optional): version of python. Defaults to "3_6".

    Raises:
        FileNotFoundError

    Returns:
        Set[str]: std library module names
    """
    FILE_LOC = os.path.join(
        os.path.dirname(__file__), "standard_library_names", f"python_{version}"
    )

    if not os.path.isfile(FILE_LOC):
        raise FileNotFoundError(FILE_LOC)

    with open(FILE_LOC) as fh:
        return set(fh.read().splitlines())


STD_LIBRARIES = get_standard_library_modules()


def module_segmenter(module_names: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """Implementation of a segmenter. Segmentation is decided by the name of the modules and provided information about the environments std
    library and packaged modules.

    Args:
        module_names (List[str]): modules to segment
        standard_library (Set[str]): std library module names
        packaged_modules (Set[str]): packaged module names

    Raises:
        Exception: Can not Segment

    Returns:
        Tuple[List[str], List[str], List[str]]: Relative Modules, Packaged Modules, Std Library Modules
    """
    rv_relative_modules = []
    rv_packaged_modules = []
    rv_std_library_modules = []

    for module_name in module_names:
        if module_name[0] == ".":
            rv_relative_modules.append(module_name)

        elif module_name in STD_LIBRARIES:
            rv_std_library_modules.append(module_name)

        elif DistributionEnvironment.is_module_in_distribution(module_name):
            rv_packaged_modules.append(module_name)

        else:
            raise Exception(f"Error with packaging module '{module_name}'.")

    return rv_relative_modules, rv_packaged_modules, rv_std_library_modules
