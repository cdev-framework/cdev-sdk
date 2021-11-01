import hashlib
from typing import List

from pydantic.types import FilePath


"""
These functions provide the a 'standardized' way of producing hashes to identify uniqueness. These hash functions are **not**
cryptographically secure and should not be used for that. Instead, these functions should simply be used to create hashes
that will be used to track changes throughout the system. 
"""


def hash_list(val: List[str]) -> str:
    if not val:
        return "0"
        
    return hash_string("".join([str(x) for x in val]))


def hash_string(val: str) -> str:
    return hashlib.md5(val.encode()).hexdigest() 


def hash_file(fp: FilePath) -> str:
    with open(fp, "r") as fh:
        hash = hashlib.md5(fh.read().encode()).hexdigest()

    return hash



def hash_zipfile(fp: FilePath) -> str:
    with open(fp, "rb") as fh:
        m = hashlib.md5()
        data = fh.read()
        m.update(data)
        hash = m.hexdigest()

    return hash