from typing import Any, Dict

from pydantic import FilePath


_ALL_CACHES = {}


def get_cache(cache_name: str) -> "Cache":
    """Get a registered Cache by name

    Args:
        cache_name (str): name of Cache

    Raises:
        Exception: Cache does not exist

    Returns:
        Cache
    """
    if cache_name not in _ALL_CACHES:
        raise Exception(f"Cache {cache_name} does not exist")

    return _ALL_CACHES.get(cache_name)


def register_cache(cache_name: str, cache: "Cache") -> None:
    """Register a Cache by name

    Args:
        cache_name (str): cache name
        cache (Cache): cache

    Raises:
        Exception: Cache name already registered
    """

    if cache_name in _ALL_CACHES:
        raise Exception(f"Cache {cache_name} already exists")

    _ALL_CACHES[cache_name] = cache


class Cache:
    """Base API for a Cache to implement"""

    def in_cache(self, key: str) -> bool:
        """Check whether a given key exists in the Cache

        Args:
            key (str)

        Returns:
            bool
        """
        raise NotImplementedError

    def get_from_cache(self, key: str) -> Any:
        """Get a value from the Cache by the key

        Args:
            key (str)

        Returns:
            Any: value
        """
        raise NotImplementedError

    def update_cache(self, key: str, val: Any) -> None:
        """Update a <key,value> in the Cache

        Args:
            key (str): update key
            val (Any): updated value
        """
        raise NotImplementedError


class InMemoryCache(Cache):
    """Cache backed by a in memory dictionary"""

    def __init__(self, initial_data: Dict = None) -> None:
        super().__init__()
        self._cache_data = initial_data or {}

    def in_cache(self, key: str) -> bool:
        return key in self._cache_data

    def get_from_cache(self, key: str) -> Any:
        return self._cache_data.get(key)

    def update_cache(self, key: str, val: Any):
        self._cache_data[key] = val


class FileLoadableCache(InMemoryCache):
    """InMemoryCache that can be loaded from a given file. Also provides function to dump contents to file."""

    def __init__(self, fp: FilePath) -> None:
        self.fp = fp
        data = self._load_from_file(fp)
        super().__init__(data)

    def dump_to_file(self) -> None:
        """Dump the contents of the Cache into the file"""
        raise NotImplementedError

    def _load_from_file(self) -> Dict:
        """Internal function to implement loading the data from a file

        Returns:
            Dict: data
        """
        raise NotImplementedError
