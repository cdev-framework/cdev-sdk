import json
from jsonschema import Draft7Validator, RefResolver
import os

class SCHEMA:
    BACKEND_LAMBDA = "BACKEND_LAMBDA"
    BACKEND_RESOURCE = "BACKEND_RESOURCE"
    FRONTEND_FUNCTION = "FRONTEND_FUNCTION"



REFERENCE_NAMES = set([
    "BACKEND_LAMBDA",
    "FRONTEND_FUNCTION"
])


_VALIDATORS = {}

BACKEND_PATH = os.path.join(os.path.dirname(__file__), "backend")
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "frontend")

ALL_PATHS = [BACKEND_PATH, FRONTEND_PATH]


def _init():
    for path in ALL_PATHS:
        _load_validators(path)


def _load_validators(path):
    child_dirs = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

    # Also load schema in the parent dir (these are the reused schema)
    child_dirs.append(path)

    for d in child_dirs:
        base_files = [f for f in os.listdir(os.path.join(path,d)) if os.path.isfile(os.path.join(path, d, f))]

        for file_name in base_files:
            broken_name = file_name.split(".")
            
            # TODO do error handling
            if broken_name[-1] != "json" and broken_name[-2] != "schema":
                continue

            with open(os.path.join(path, d, file_name)) as fh:
                schema_obj = json.load(fh)

            resolver = RefResolver("file://" + os.path.join(path, d, file_name), schema_obj)

            validator = Draft7Validator(schema_obj, resolver=resolver)

            _VALIDATORS[schema_obj['reference_name']] = validator


def validate(schema_name, object):
    if schema_name in _VALIDATORS:
        _VALIDATORS.get(schema_name).validate(object)


_init()
