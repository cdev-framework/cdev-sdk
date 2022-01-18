from sortedcontainers.sorteddict import SortedDict

import collections


class FrozenDict(collections.Mapping):

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
        if not (isinstance(v, FrozenDict)) :
            raise TypeError(f'{v} Not Frozen Dict')


    
    def __repr__(self) -> str:
        return f"FrozenDict({self._d})"
        
    #def __hash__(self):
    #    
    #    return hash(frozenset(self.items()))