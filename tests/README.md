# Cdev Testing

This folder contains all the unit tests for Cdev framework. This folders only contains unit tests for the different modules that make up the Cdev framework. Some parts of the framework can not be easily tested with standard unit test. Those parts are listed at the end and contain info how to test changes made to them

Cdev uses [pytest](https://docs.pytest.org/en/6.2.x/) and tries to keep the testing simple to make it easy for anyone to contribute and add new test cases. Later it might be nessicary to add a more complex testing framework.

To run the whole test suite run the following command from the root of the project:
```
./scripts/run_unit_test
```
To run individual test use pytest from the command line in the /src folder

# Schema
'schema_test.py'

Each schema used in the project should contain two json files in the 'example_schema' folder: one file for correct json and one for incorrect. Each file should itself be a json that contains a list called 'tests'. The items in the list should be the json objects that need to be tested.

The test file runs through a list that contains all the testing information as a list of triplets:
    - test_file_location:
    - schema
    - should_pass

To add a new test simply create a new json file in the 'example_schema' folder and add a new triplet.

# Parser
'parser_test.py'

Contains test for the cdev function parser. It runs through example files that contain functions that need to be parsed out with all their dependencies.

*** IF YOU CHANGE ANY PART OF THE EXAMPLE FILES TESTS WILL FAIL ***
