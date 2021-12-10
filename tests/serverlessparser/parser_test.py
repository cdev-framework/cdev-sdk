import os
import sys

sys.path.append(os.path.join("."))


EXAMPLE_PATH = os.path.join(".", "tests", "example_python_files")

ADVANCED_PATH = os.path.join(EXAMPLE_PATH, "advanced")
SIMPLE_PATH = os.path.join(EXAMPLE_PATH, "simple")

""" def test_example1_all_functions():
    test_file_name = "example1.py"
    fp = os.path.join(ADVANCED_PATH , test_file_name)

    assert os.path.isfile(fp)

    # Needed line numbers with no manual imports
    results = {
        "f1": [[1, 1], [12, 13], [14, 21]],
        "t_function": [[1, 1], [2, 3], [4, 5], [7, 8], [9, 9], [10, 11], [12, 13], [14, 21], [22, 28]],
        "b": [[1, 1], [2, 3], [4, 5], [7, 8], [9, 9], [10, 11], [12, 13], [14, 21], [22, 28], [29, 31]]
    }

    try:
        rv = cp.parse_functions_from_file(fp)
        
        print(rv.parsed_functions)
        assert len(rv.parsed_functions) == 3

        for f in rv.parsed_functions:
            if not f.name in results:
                # The parsed function was not in the results
                assert False
                continue
            print(f"{f.name}: {f.get_line_numbers()}")
            assert f.get_line_numbers() == results.get(f.name)

    except Exception as e:
        assert False


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
        assert False """