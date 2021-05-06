import os

import src.cdev.parser.cdev_parser as cp

EXAMPLE_PATH = os.path.join(".", "tests", "example_files")

SIMPLE_PATH = os.path.join(EXAMPLE_PATH, "simple")

def test_demo():
    test_file_name = "basic.py"
    fp = os.path.join(SIMPLE_PATH, test_file_name) #filepath
    assert os.path.isfile(fp)


def test_no_imports_basic():
    test_file_name = "basic.py"
    fp = os.path.join(SIMPLE_PATH, test_file_name)

    assert os.path.isfile(fp)

    try:
        rv = cp.parse_functions_from_file(fp)
        
        print(rv.parsed_functions)
        assert len(rv.parsed_functions) == 1

        assert rv.parsed_functions[0].get_line_numbers() == [[1,4]]

    except Exception as e:
        assert False


def test_global_symbols_basic():
    test_file_name = "global_vars.py"
    fp = os.path.join(SIMPLE_PATH, test_file_name)

    assert os.path.isfile(fp)

    try:
        rv = cp.parse_functions_from_file(fp)
        
        print(rv.parsed_functions)
        assert len(rv.parsed_functions) == 1

        print(rv.parsed_functions[0].get_line_numbers())
        assert rv.parsed_functions[0].get_line_numbers() == [[4,5], [6,9]]

    except Exception as e:
        assert False


def test_import_symbols_basic():
    test_file_name = "import_vars.py"
    fp = os.path.join(SIMPLE_PATH, test_file_name)

    assert os.path.isfile(fp)

    try:
        rv = cp.parse_functions_from_file(fp)
        
        print(rv.parsed_functions)
        assert len(rv.parsed_functions) == 1

        print(rv.parsed_functions[0].get_line_numbers())
        assert rv.parsed_functions[0].get_line_numbers() == [[1,1], [2,4], [5,9]]

    except Exception as e:
        assert False
