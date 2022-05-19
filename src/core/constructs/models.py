"""Set of utilities for working with immutable data within the framework
"""
from collections.abc import Mapping
from enum import Enum
from pydantic import BaseModel

from pydantic.utils import (
    ROOT_KEY,
    ValueItems,
    sequence_like,
)

from pydantic.typing import (
    is_namedtuple,
)

from typing import Any


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

        if not (isinstance(v, frozendict)):

            raise TypeError(f"{v} Not Frozen Dict")

        return v

    def __repr__(self) -> str:
        return f"FrozenDict({self._d})"


class ImmutableModel(BaseModel):
    @classmethod
    def _get_value(
        cls,
        v: Any,
        to_dict: bool,
        by_alias: bool,
        include,
        exclude,
        exclude_unset: bool,
        exclude_defaults: bool,
        exclude_none: bool,
    ) -> Any:

        if isinstance(v, BaseModel):
            if to_dict:
                v_dict = frozendict(
                    v.dict(
                        by_alias=by_alias,
                        exclude_unset=exclude_unset,
                        exclude_defaults=exclude_defaults,
                        include=include,
                        exclude=exclude,
                        exclude_none=exclude_none,
                    )
                )
                if ROOT_KEY in v_dict:
                    return v_dict[ROOT_KEY]
                return v_dict
            else:
                return v.copy(include=include, exclude=exclude)

        value_exclude = ValueItems(v, exclude) if exclude else None
        value_include = ValueItems(v, include) if include else None

        if isinstance(v, dict):
            return frozendict(
                {
                    k_: cls._get_value(
                        v_,
                        to_dict=to_dict,
                        by_alias=by_alias,
                        exclude_unset=exclude_unset,
                        exclude_defaults=exclude_defaults,
                        include=value_include and value_include.for_element(k_),
                        exclude=value_exclude and value_exclude.for_element(k_),
                        exclude_none=exclude_none,
                    )
                    for k_, v_ in v.items()
                    if (not value_exclude or not value_exclude.is_excluded(k_))
                    and (not value_include or value_include.is_included(k_))
                }
            )

        elif sequence_like(v):
            seq_args = (
                cls._get_value(
                    v_,
                    to_dict=to_dict,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    include=value_include and value_include.for_element(i),
                    exclude=value_exclude and value_exclude.for_element(i),
                    exclude_none=exclude_none,
                )
                for i, v_ in enumerate(v)
                if (not value_exclude or not value_exclude.is_excluded(i))
                and (not value_include or value_include.is_included(i))
            )

            return (
                v.__class__(*seq_args)
                if is_namedtuple(v.__class__)
                else v.__class__(seq_args)
            )

        elif isinstance(v, Enum) and getattr(cls.Config, "use_enum_values", False):
            return v.value

        else:
            return v

    class Config:
        extra = "allow"
        frozen = True
