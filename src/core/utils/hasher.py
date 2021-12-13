import hashlib
from typing import List

from pydantic.types import FilePath


"""
These functions provide the a 'standardized' way of producing hashes to identify uniqueness. These hash functions are **not**
cryptographically secure and should not be used for that. Instead, these functions should simply be used to create hashes
that will be used to track changes throughout the system. 
"""

class FILE_CACHE_CLASS:
    cache = {}

FILE_CACHE = FILE_CACHE_CLASS()

def hash_list(val: List[str]) -> str:
    if not val:
        return "0"
        
    return hash_string("".join([str(x) for x in val]))


def hash_string(val: str) -> str:
    return hashlib.md5(val.encode()).hexdigest() 


def clear_file_cache():
    FILE_CACHE.cache = {}


def hash_file(fp: FilePath) -> str:
    if fp in FILE_CACHE.cache:
        return FILE_CACHE.cache.get(fp)

    with open(fp, "rb") as fh:
        hash = hashlib.md5(fh.read()).hexdigest()

    FILE_CACHE.cache[fp] = hash

    return hash



