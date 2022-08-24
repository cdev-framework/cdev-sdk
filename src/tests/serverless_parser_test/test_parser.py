import os
import sys

from serverless_parser.parser import parse_functions_from_file

EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "example_python_files")

ADVANCED_PATH = os.path.join(EXAMPLE_PATH, "advanced")
SIMPLE_PATH = os.path.join(EXAMPLE_PATH, "simple")

# Note that in Python3.8 the AST module changed how it associated whitespace lines to <stmts>
# therefor, the parser will return slightly different values for python3.7 compared to any version
# after python3.8


def test_example1_all_functions():
    fp = os.path.join(ADVANCED_PATH, "example1.py")

    assert os.path.isfile(fp)

    # Needed line numbers with no manual imports
    py_37_results = {
        "f1": [[12, 14], [15, 21]],
        "t_function": [
            [1, 1],
            [2, 3],
            [4, 5],
            [6, 6],
            [7, 8],
            [9, 9],
            [10, 11],
            [12, 14],
            [15, 21],
            [22, 28],
        ],
        "b": [
            [1, 1],
            [2, 3],
            [4, 5],
            [6, 6],
            [7, 8],
            [9, 9],
            [10, 11],
            [12, 14],
            [15, 21],
            [22, 28],
            [29, 31],
        ],
    }

    py_38_results = {
        "f1": [[12, 12], [15, 19]],
        "t_function": [
            [1, 1],
            [2, 2],
            [4, 4],
            [6, 6],
            [7, 7],
            [9, 9],
            [10, 10],
            [12, 12],
            [15, 19],
            [22, 26],
        ],
        "b": [
            [1, 1],
            [2, 2],
            [4, 4],
            [6, 6],
            [7, 7],
            [9, 9],
            [10, 10],
            [12, 12],
            [15, 19],
            [22, 26],
            [29, 30],
        ],
    }

    results = py_37_results if sys.version_info.minor == 7 else py_38_results

    try:
        rv = parse_functions_from_file(fp)

        assert len(rv.parsed_functions) == 3

        for f in rv.parsed_functions:
            if not f.name in results:
                # The parsed function was not in the results
                assert False

            res = list(f.get_line_numbers())
            print(res)
            assert res == results.get(f.name)

    except Exception as e:
        assert False


def test_no_imports_basic():
    fp = os.path.join(SIMPLE_PATH, "basic.py")

    assert os.path.isfile(fp)

    py_37_result = [[1, 4]]
    py_38_result = [[1, 3]]

    result = py_37_result if sys.version_info.minor == 7 else py_38_result

    try:
        rv = parse_functions_from_file(fp)

        assert len(rv.parsed_functions) == 1

        assert rv.parsed_functions[0].get_line_numbers() == result

    except Exception as e:
        assert False


def test_global_symbols_basic():
    fp = os.path.join(SIMPLE_PATH, "global_vars.py")

    assert os.path.isfile(fp)

    py_37_result = [[4, 6], [7, 10]]
    py_38_result = [[4, 4], [7, 9]]

    result = py_37_result if sys.version_info.minor == 7 else py_38_result

    try:
        rv = parse_functions_from_file(fp)

        assert len(rv.parsed_functions) == 1

        res = list(rv.parsed_functions[0].get_line_numbers())
        assert res == result

    except Exception as e:
        assert False


def test_import_symbols_basic():
    fp = os.path.join(SIMPLE_PATH, "import_vars.py")

    assert os.path.isfile(fp)

    py_37_result = [[1, 1], [2, 4], [5, 9]]
    py_38_result = [[1, 1], [2, 2], [5, 8]]

    result = py_37_result if sys.version_info.minor == 7 else py_38_result

    try:
        rv = parse_functions_from_file(fp)

        assert len(rv.parsed_functions) == 1

        res = list(rv.parsed_functions[0].get_line_numbers())
        assert res == result

    except Exception as e:
        assert False
