import os
from core.utils.fs_manager import handler_optimizer
from core.constructs.settings import Settings
from core.constructs.workspace import Workspace

tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")


settings = Settings()
settings.BASE_PATH = tmp_dir
settings.INTERMEDIATE_FOLDER_LOCATION = tmp_dir


ws = Workspace()
ws.settings = settings


DATA_BASEPATH = os.path.join(os.path.dirname(__file__), "test_data")


def test_create_optimized_handler_artifact():
    assert True


def test_create_intermediate_handler_file():
    assert True


def test_make_additional_file_information():
    base_path = os.path.join(DATA_BASEPATH, "relative_handler_modules")
    test_data = [
        (
            (os.path.join(base_path, "vamos"), base_path),
            [
                (os.path.join(base_path, "vamos", "__init__.py"), "vamos/__init__.py"),
                (os.path.join(base_path, "vamos", "tmp.py"), "vamos/tmp.py"),
            ],
        )
    ]

    for datum in test_data:
        assert set(datum[1]) == set(
            handler_optimizer._make_additional_file_information(*datum[0])
        )


def test_get_file_as_list():
    test_files_path = os.path.join(DATA_BASEPATH, "parse_files")

    test_data = [
        (
            os.path.join(test_files_path, "tmp.py"),
            [
                "import os",
                "",
                'x = "hello"',
                "print(x)",
                "",
                "",
                "def y():",
                '    print("here")',
                "",
                "",
                "# Some comment",
            ],
        )
    ]

    for datum in test_data:
        assert datum[1] == handler_optimizer._get_file_as_list(datum[0])


def test_clean_lines():
    test_data = [
        (
            [
                "import os",
                'x = "hello"',
                "print(x)",
                "",
                "def y():",
                '    print("here")',
                "",
                "",
                "#Some comment",
            ],
            [
                "import os",
                'x = "hello"',
                "print(x)",
                "",
                "def y():",
                '    print("here")',
            ],
        )
    ]

    for datum in test_data:
        assert datum[1] == handler_optimizer._clean_lines(datum[0])


def test_get_lines_from_file_list():
    test_data = [
        (
            (
                [
                    "import os",
                    'x = "hello"',
                    "print(x)",
                    "",
                    "def y():",
                    '    print("here")',
                    "",
                    "",
                    "#Some comment",
                ],
                [1, 2, 3, 6],
            ),
            ["import os", 'x = "hello"', "print(x)", '    print("here")'],
        )
    ]

    for datum in test_data:
        assert datum[1] == handler_optimizer._get_lines_from_file_list(*datum[0])


def test_write_intermediate_function():
    assert True


def test_get_relative_path():
    data = [(("/home/daniel/tmp/a", "/home/daniel/"), "tmp/a")]

    for datum in data:
        assert datum[1] == handler_optimizer._get_relative_path(*datum[0])
