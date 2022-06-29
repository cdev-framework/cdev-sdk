import os

from core.constructs.components import ComponentModel
from core.constructs.models import frozendict
from core.constructs.resource import ResourceModel
from core.constructs.resource_state import Resource_State

from core.utils.file_manager import (
    _load_cloud_output_operations,
    _recursive_make_immutable,
    safe_json_write,
    load_resource_state,
)

_resource_state = Resource_State(
    "demo1",
    "1234",
    components=[
        ComponentModel(
            "name",
            "123",
            resources=[ResourceModel(name="r1", ruuid="r", hash="12345", val="val")],
        )
    ],
)

tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
sample_json_dir = os.path.join(os.path.dirname(__file__), "test_data")


def test_safe_json_write():
    safe_json_write(
        _resource_state.dict(), os.path.join(tmp_dir, "safe_json_test.json")
    )


def test_load_resource_state():
    fp = os.path.join(sample_json_dir, "sample_resource_state.json")

    assert load_resource_state(fp) == _resource_state


def test_recursive_make_immutable():
    d = {
        "ruuid": "r",
        "name": "r1",
        "hash": "1",
        "vals": [
            {"k": "v"},
            {"k1": "v1"},
            {
                "id": "cdev_cloud_output",
                "output_operations": [["fun1", [1, 2, 3], {"k": "v"}]],
            },
        ],
    }

    res = frozendict(
        {
            "ruuid": "r",
            "name": "r1",
            "hash": "1",
            "vals": frozenset(
                [
                    frozendict({"k": "v"}),
                    frozendict({"k1": "v1"}),
                    frozendict(
                        {
                            "id": "cdev_cloud_output",
                            "output_operations": tuple(
                                [
                                    tuple(
                                        [
                                            "fun1",
                                            tuple([1, 2, 3]),
                                            frozendict({"k": "v"}),
                                        ]
                                    )
                                ]
                            ),
                        }
                    ),
                ]
            ),
        }
    )

    d2 = _recursive_make_immutable(d)

    assert res == d2


def test_load_cloud_output_operations():
    d = [["fun1", [1, 2, 3], {"k": "v"}]]

    res = tuple([tuple(["fun1", tuple([1, 2, 3]), frozendict({"k": "v"})])])

    d2 = _load_cloud_output_operations(d)
    assert d2 == res
