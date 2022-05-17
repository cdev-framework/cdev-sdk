import os
import shutil
import uuid


from core.default.backend import LocalBackend

from ..constructs import backend as backend_tests

# Monkey patch the file location to be ./tmp
base_dir = os.path.join(os.path.dirname(__file__), "tmp")
# state_file = os.path.join(base_dir, "local_state.json")


def local_backend_factory() -> LocalBackend:
    tmp = str(uuid.uuid4())
    new_base = os.path.join(base_dir, tmp)
    new_state_file = os.path.join(new_base, "local_state.json")

    os.mkdir(new_base)
    return LocalBackend(new_base, new_state_file)


def test_sample():
    backend_tests.simple_actions(local_backend_factory())


def test_simple_get_resources():
    backend_tests.simple_get_resource(local_backend_factory())


def test_simple_references():
    backend_tests.simple_references(local_backend_factory())


def test_simple_exceptions():
    backend_tests.conflicting_names_resource_state(local_backend_factory())
    backend_tests.conflicting_names_component(local_backend_factory())
    backend_tests.get_missing_component(local_backend_factory())
    backend_tests.get_missing_resource(local_backend_factory())
    backend_tests.get_missing_cloud_output(local_backend_factory())


def test_simple_differencing():
    backend_tests.simple_differences(local_backend_factory())
