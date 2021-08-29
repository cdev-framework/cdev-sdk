from typing import (
    Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union
)

from enum import Enum

from pydantic import BaseModel



class CloudState(BaseModel):
    output: Dict

class CloudMapping(BaseModel):
    state: Dict[str,CloudState]
    """
    Dictionary from hash of the resource to the Cloud Resources
    """
