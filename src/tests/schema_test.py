import os
import json
import jsonschema

from cdev.schema import utils as schema_utils

# This file test the json schema system and test the different json
# schema that can be created. Any new json schema created for the project
# should include atleast 2 test. 
# 
# (eventually this will need to broken into more files)

BASE_SCHEMA_EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "example_schema")


TESTS = [
    # A test is defined as a triplet of:
    #   - Path to file to test relative to BASE_SCHEMA_EXAMPLE_PATH
    #   - schema_utils.SCHEMA that it should test against
    #   - bool: if the validation should pass 
    ("resource_good.json", schema_utils.SCHEMA.BACKEND_RESOURCE, True),
    ("resource_bad.json", schema_utils.SCHEMA.BACKEND_RESOURCE, False),
    ("lambda_good.json", schema_utils.SCHEMA.BACKEND_LAMBDA, True),
    ("lambda_bad.json", schema_utils.SCHEMA.BACKEND_LAMBDA, False),
    ("lambda_update_function_configuration_good.json", schema_utils.SCHEMA.BACKEND_LAMBDA_UPDATE_FUNCTION_CONFIGURATION, True),
    ("lambda_update_function_configuration_bad.json", schema_utils.SCHEMA.BACKEND_LAMBDA_UPDATE_FUNCTION_CONFIGURATION, False),
    ("lambda_configuration_good.json", schema_utils.SCHEMA.BACKEND_LAMBDA_CONFIGURATION, True),
    ("lambda_create_function_good.json", schema_utils.SCHEMA.BACKEND_LAMBDA_CREATE_FUNCTION, True),
    ("lambda_update_function_code_good.json", schema_utils.SCHEMA.BACKEND_LAMBDA_UPDATE_FUNCTION_CODE, True),
    ("lambda_delete_function_good.json", schema_utils.SCHEMA.BACKEND_LAMBDA_DELETE_FUNCTION, True)
]


def _load_json_from_path(fp):
    if not os.path.isfile(fp):
        raise FileNotFoundError

    with open(fp) as fh:
        rv = json.load(fh)

    return rv


def test_schema():
    for test in TESTS:
        fp = test[0]
        schema = test[1]
        should_pass = test[2]

        try:
            loaded_json = _load_json_from_path(
                os.path.join(BASE_SCHEMA_EXAMPLE_PATH, fp)
            ) 
        except Exception as e:
            assert False

        for test_case in loaded_json.get("tests"):
            try:
               
                schema_utils.validate(schema, test_case)
            except jsonschema.ValidationError as e:
                # Catch validation errors and check test case to see if it should have failed
                if should_pass:
                    print(f'FAILED AT -> {test}; {test_case}')
                    assert False

                continue
            except Exception as e:
                print(e)
                assert False


            # If it got here than it passed validation and need to check test case 
            # to see if it should have passed
            if not should_pass:
                print(f'FAILED AT -> {test}; {test_case}')
                assert False

