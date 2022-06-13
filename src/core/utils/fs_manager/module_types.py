from typing import Dict, List, Optional, Set

from pydantic.types import FilePath
from pydantic import BaseModel
from enum import Enum


class ModuleInfo(BaseModel):
    module_name: str
    absolute_fs_position: Optional[str]
    is_dir: Optional[bool]

    def to_key(self):
        return ";".join(
            (self.module_name, str(self.absolute_fs_position), str(self.is_dir))
        )

    def __eq__(self, other):
        if not isinstance(other, ModuleInfo):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.to_key() == other.to_key()

    def __hash__(self):
        return hash(self.to_key())


class StdLibModuleInfo(ModuleInfo):
    pass


class PackagedModuleInfo(ModuleInfo):
    tag: str


class RelativeModuleInfo(ModuleInfo):
    pass
