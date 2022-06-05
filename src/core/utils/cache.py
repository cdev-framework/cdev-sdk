from typing import Any, Dict

from pydantic import FilePath


_ALL_CACHES = {}


def get_cache(cache_name: str) -> "Cache":
    if cache_name not in _ALL_CACHES:
        raise Exception(f"Cache {cache_name} does not exist")

    return _ALL_CACHES.get(cache_name)


def register_cache(cache_name: str, cache: "Cache"):

    if cache_name in _ALL_CACHES:
        raise Exception(f"Cache {cache_name} already exists")

    _ALL_CACHES[cache_name] = cache


class Cache:
    def in_cache(self, key: str) -> bool:
        raise NotImplementedError

    def get_from_cache(self, key: str) -> str:
        raise NotImplementedError

    def update_cache(self, key: str, val: Any):
        raise NotImplementedError


class InMemoryCache(Cache):
    def __init__(self, initial_data: Dict = None) -> None:
        super().__init__()
        self._cache_data = initial_data if initial_data else {}

    def in_cache(self, key: str) -> bool:
        return key in self._cache_data

    def get_from_cache(self, key: str) -> Any:
        return self._cache_data.get(key)

    def update_cache(self, key: str, val: Any):
        self._cache_data[key] = val


class FileLoadableCache(InMemoryCache):
    def __init__(self, fp: FilePath = None) -> None:
        if not fp:
            super().__init__()
            return

        data = self._load_from_file(fp)
        super().__init__(data)
        self.fp = fp

    def dump_to_file(self) -> None:
        raise NotImplementedError

    def _load_from_file(self, fp: FilePath) -> Dict:
        raise NotImplementedError
