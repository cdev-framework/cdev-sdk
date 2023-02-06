from pathlib import Path
from typing import List, Set, Tuple
from pydantic import DirectoryPath, FilePath

from .utils import module_segmenter
from .relative_generator import (
    get_all_relative_module_dependencies,
    _compute_relative_dependency_module,
)


def get_all_dependencies(
    original_file: DirectoryPath, imported_modules: List[str]
) -> Tuple[Set[str], Set[str]]:

    relative_modules, packaged_modules, _ = module_segmenter(imported_modules)
    relative_relative_modules = set()
    relative_packaged_modules = set()

    base_directory = Path(original_file).parent

    for relative_module in relative_modules:
        relative_fp = _compute_relative_dependency_module(
            relative_module, base_directory
        )
        relative_rv, packaged_rv, _ = get_all_relative_module_dependencies(relative_fp)

        relative_relative_modules.update(relative_rv)
        relative_packaged_modules.update(packaged_rv)

    rv_relatives = set(
        [
            _compute_relative_dependency_module(x, base_directory)
            for x in relative_modules
        ]
    )
    rv_relatives.update(relative_relative_modules)

    rv_packaged = set(packaged_modules)
    rv_packaged.update(relative_packaged_modules)

    return (rv_relatives, rv_packaged)
