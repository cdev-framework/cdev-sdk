"""Utilities to provide a 'standardized' way of producing hashes to identify uniqueness.

These hash functions are **not**
cryptographically secure and should not be used for that. Instead, these functions should simply be used to create hashes
that will be used to track changes throughout the system.
"""

import hashlib
import os
from typing import List, Union

from pydantic.types import FilePath

from core.utils.exceptions import cdev_core_error


class FILE_CACHE_CLASS:
    cache = {}


FILE_CACHE = FILE_CACHE_CLASS()


def hash_list(val: List[str], deliminator: str = ";") -> str:
    """Hash a list of str values

    Note that the order of the list also determines the output, therefore if the input is stored in
    an unsorted collection, you should used `hash_set` instead.

    Args:
        val (List[str]): The list of str to produce a hash of
        deliminator (Optional[str]): A value use to seperate the input. Defaults to ';'

    Returns:
        str: hash of the values
    """

    return hash_string(deliminator.join([str(x) for x in val]))


def hash_string(val: str) -> str:
    """Hash a str value

    Implemented using md5.

    Args:
        val (str): value to hash

    Returns:
        str: hash of the value
    """
    return hashlib.md5(val.encode()).hexdigest()


def clear_file_cache() -> None:
    """Clear the cache used by the `hash_file` utility."""
    FILE_CACHE.cache = {}


def hash_file(fp: Union[FilePath, str], bypass_cache: bool = False) -> str:
    """Hash a file given a path

    Note that the implementation contains a reference to a cache. Since this utility is primarily
    used as an internal tool with the framework, the cache helps speeds things up when we know the file has
    not changed. Note that the framework periodically flushes this cache when needed within the context of
    the execution of the framework using the `clear_file_cache` function.

    If using this outside the confides of the framework, you can by pass the cache by setting the `bypass_cache`
    flag.

    Note that the implementation returns a md5 hash of the bytes in the file.

    Args:
        fp (FilePath): Path to the file. Must be a resolvable path on the filesystem.
        bypass_cache (Optional[bool]): By pass the internal cache. Default False.

    Returns:
        str: hash of the file

    Raises:
        Cdev_Error
    """
    if fp in FILE_CACHE.cache and not bypass_cache:
        return FILE_CACHE.cache.get(fp)

    if not os.path.isfile(fp):
        raise cdev_core_error(f"Could not find file ({fp}) to hash", FileNotFoundError)

    with open(fp, "rb") as fh:
        the_hash = hashlib.md5(fh.read()).hexdigest()

    FILE_CACHE.cache[fp] = the_hash

    return the_hash
