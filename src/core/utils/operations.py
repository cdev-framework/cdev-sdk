import itertools
from typing import Any, Dict, List
from functools import reduce


def concatenate(lists: List[List[Any]]) -> List[Any]:
    """Function that flattens a list of list into a single list.

    Args:
        lists (List[List[Any]])

    Returns:
        List[Any]
    """
    return list(itertools.chain.from_iterable(lists))


def combine_dictionaries(dicts: List[Dict]) -> Dict:
    """Function that flattens a list of Dict into a single Dictionary. Note that ordering of the list matters,
    because keys will overwrite each other.

    Args:
        dicts (List[Dict])

    Returns:
        Dict
    """
    if not input:
        return {}

    return reduce(lambda a, b: {**a, **b}, dicts)
