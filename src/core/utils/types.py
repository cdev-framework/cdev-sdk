from sortedcontainers.sorteddict import SortedDict

from collections.abc import Mapping


class frozendict(Mapping):

    def __init__(self, d: dict):
        self._d = d

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __hash__(self):
        return hash(tuple(sorted(self._d.items())))

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        
        if not (isinstance(v, frozendict)) :
            
            raise TypeError(f'{v} Not Frozen Dict')

        return v
    
    def __repr__(self) -> str:
        return f"FrozenDict({self._d})"
        
