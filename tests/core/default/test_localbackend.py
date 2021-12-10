import os

from core.default.backend import LocalBackend

from ..constructs import backend as backend_tests

# Monkey patch the file location to be ./tmp
base_dir = os.path.join(os.path.dirname(__file__), "tmp")
state_file = os.path.join(base_dir, "local_state.json")

# Delete any files in the tmp directory before running
for f in os.listdir(base_dir):
    os.remove(os.path.join(base_dir, f))



mybackend = LocalBackend(base_dir, state_file)


def test_sample():
    backend_tests.simple_actions(mybackend)


def test_simple_get_resources():
    backend_tests.simple_get_resource(mybackend)