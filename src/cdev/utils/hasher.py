import hashlib
from typing import List


"""
These functions provide the a 'standardized' way of producing hashes to identify uniqueness. These hash functions are **not**
cryptographically secure and should not be used for that. Instead, these functions should simply be used to create hashes
that will be used to track changes throughout the system. 
"""


def hash_list(val: List[str]) -> str:
    return hash_string("".join(val))

def hash_string(val: str) -> str:
    return hashlib.md5(val.encode()).hexdigest() 