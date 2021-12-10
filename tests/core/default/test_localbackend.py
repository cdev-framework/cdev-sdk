import os
import shutil
import uuid


from core.default.backend import LocalBackend

from ..constructs import backend as backend_tests

# Monkey patch the file location to be ./tmp
base_dir = os.path.join(os.path.dirname(__file__), "tmp")
#state_file = os.path.join(base_dir, "local_state.json")

# Delete any files in the tmp directory before running
for f in os.listdir(base_dir):
    item = os.path.join(base_dir, f)
    if os.path.isdir(item):
        shutil.rmtree(item)
    
    if os.path.isfile(item):
        os.remove(item)


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