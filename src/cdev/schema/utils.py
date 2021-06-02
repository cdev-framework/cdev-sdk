import json
import os


ALL_SCHEMA = {
    "FUNCTION": os.path.join(os.path.dirname( __file__ ),"function.json"),
}

def get_schema(schema_name):
    # TODO throw errors
    if not schema_name in ALL_SCHEMA:
        return None

    if not os.path.isfile(ALL_SCHEMA.get(schema_name)):
        return None

    with open(ALL_SCHEMA.get(schema_name)) as fh:
        rv = json.load(fh)

    return rv