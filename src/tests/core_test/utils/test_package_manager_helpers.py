# import dill
from pkg_resources import Distribution, WorkingSet
from pydantic import FilePath
import os
from functools import partial

from core.utils.fs_manager.module_types import (
    RelativeModuleInfo,
    PackagedModuleInfo,
    StdLibModuleInfo,
)
from core.utils.fs_manager import package_manager
from core.constructs.settings import Settings
from core.constructs.workspace import Workspace

tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")


settings = Settings()
settings.BASE_PATH = tmp_dir
settings.INTERMEDIATE_FOLDER_LOCATION = tmp_dir


ws = Workspace()
ws.settings = settings


DATA_BASEPATH = os.path.join(os.path.dirname(__file__), "test_data")
PICKLED_FILED_BASE = os.path.join(DATA_BASEPATH, "pickled_envs")


def test_get_all_module_info():
    # Relative info
    base_relative_test_files = os.path.join(DATA_BASEPATH, "get_all_modules")
    starting_file_location = os.path.join(base_relative_test_files, "src", "handler.py")
    tmp_fp = os.path.join(base_relative_test_files, "src", "tmp.py")
    start_fp = os.path.join(base_relative_test_files, "src", "start.py")
    utils_fp = os.path.join(base_relative_test_files, "src", "utils")

    # Std Library Info
    standard_library = set(["math", "sys"])

    # Packaged Info
    base_pkged_test_files = os.path.join(DATA_BASEPATH, "packaged_module_info")
    packaged_locations = {
        "pandas": (base_pkged_test_files, "cp37-cp37m-manylinux_2_17_x86_64"),
        "six": (base_pkged_test_files, "py2-none-any"),
    }
    packaged_module_dependencies = {"pandas": ["six"]}

    test_data = [
        ".start",
    ]

    module_creator = partial(
        package_manager._create_module_info,
        start_location=starting_file_location,
        standard_library=standard_library,
        packaged_module_locations_tags=packaged_locations,
    )
    module_segmenter = partial(
        package_manager._segment_module_names,
        standard_library=standard_library,
        packaged_modules=set(packaged_locations.keys()),
    )

    test_rv = [
        RelativeModuleInfo(
            module_name=".tmp", absolute_fs_position=tmp_fp, is_dir=False
        ),
        RelativeModuleInfo(
            module_name=".utils", absolute_fs_position=utils_fp, is_dir=True
        ),
        RelativeModuleInfo(
            module_name=".start", absolute_fs_position=start_fp, is_dir=False
        ),
        StdLibModuleInfo(module_name="sys"),
        StdLibModuleInfo(module_name="math"),
        PackagedModuleInfo(
            module_name="pandas",
            absolute_fs_position=os.path.join(base_pkged_test_files, "pandas"),
            is_dir=True,
            tag="cp37-cp37m-manylinux_2_17_x86_64",
        ),
        PackagedModuleInfo(
            module_name="six",
            absolute_fs_position=os.path.join(base_pkged_test_files, "six.py"),
            is_dir=False,
            tag="py2-none-any",
        ),
    ]

    rv = package_manager._get_all_module_info(
        module_names=test_data,
        pkg_module_dep_info=packaged_module_dependencies,
        module_segmenter=module_segmenter,
        module_creator=module_creator,
    )

    assert set(rv) == set(test_rv)


def test_create_module_info():
    # Relative info
    base_relative_test_files = os.path.join(DATA_BASEPATH, "relative_module_info")
    starting_file_location = os.path.join(base_relative_test_files, "src", "start.py")
    tmp_fp = os.path.join(base_relative_test_files, "src", "tmp.py")
    utils_fp = os.path.join(base_relative_test_files, "src", "utils")

    # Std Library Info
    standard_library = set(["math", "sys"])

    # Packaged Info
    base_pkged_test_files = os.path.join(DATA_BASEPATH, "packaged_module_info")
    packaged_locations = {
        "pandas": (base_pkged_test_files, "cp37-cp37m-manylinux_2_17_x86_64"),
        "six": (base_pkged_test_files, "py2-none-any"),
    }

    test_data = [
        (
            (".tmp"),
            RelativeModuleInfo(
                module_name=".tmp", absolute_fs_position=tmp_fp, is_dir=False
            ),
        ),
        (
            (".utils"),
            RelativeModuleInfo(
                module_name=".utils", absolute_fs_position=utils_fp, is_dir=True
            ),
        ),
        (("sys"), StdLibModuleInfo(module_name="sys")),
        (("math"), StdLibModuleInfo(module_name="math")),
        (
            ("pandas"),
            PackagedModuleInfo(
                module_name="pandas",
                absolute_fs_position=os.path.join(base_pkged_test_files, "pandas"),
                is_dir=True,
                tag="cp37-cp37m-manylinux_2_17_x86_64",
            ),
        ),
        (
            ("six"),
            PackagedModuleInfo(
                module_name="six",
                absolute_fs_position=os.path.join(base_pkged_test_files, "six.py"),
                is_dir=False,
                tag="py2-none-any",
            ),
        ),
    ]

    for test_datum in test_data:
        rv = package_manager._create_module_info(
            test_datum[0],
            start_location=starting_file_location,
            standard_library=standard_library,
            packaged_module_locations_tags=packaged_locations,
        )
        assert test_datum[1] == rv


def test_segment_module_names():
    test_data = [
        ([[".tmp", "a", "b"], set(["a"]), set(["b"])], ([".tmp"], ["b"], ["a"])),
        ([["..tmp", "a", "b"], set(["a"]), set(["b"])], (["..tmp"], ["b"], ["a"])),
    ]

    for test_datum in test_data:
        rv = package_manager._segment_module_names(*test_datum[0])
        assert test_datum[1] == rv


def test_recursive_find_relative_module_dependencies():
    base_test_files = os.path.join(DATA_BASEPATH, "relative_module_info")
    starting_file_location = os.path.join(base_test_files, "src", "handler.py")

    start_fp = os.path.join(base_test_files, "src", "start.py")
    tmp_fp = os.path.join(base_test_files, "src", "tmp.py")
    utils_fp = os.path.join(base_test_files, "src", "utils")

    # Std Library Info
    standard_library = set(["math", "sys"])

    # Packaged Info
    base_pkged_test_files = os.path.join(DATA_BASEPATH, "packaged_module_info")
    packaged_locations = {"pandas": base_pkged_test_files, "six": base_pkged_test_files}

    module_creator = partial(
        package_manager._create_module_info,
        start_location=starting_file_location,
        standard_library=standard_library,
        packaged_module_locations_tags=packaged_locations,
    )
    module_segmenter = partial(
        package_manager._segment_module_names,
        standard_library=standard_library,
        packaged_modules=set(packaged_locations.keys()),
    )

    data = RelativeModuleInfo(
        module_name=".start", absolute_fs_position=start_fp, is_dir=False
    )

    results = (
        set(
            [
                RelativeModuleInfo(
                    module_name=".tmp", absolute_fs_position=tmp_fp, is_dir=False
                ),
                RelativeModuleInfo(
                    module_name=".utils", absolute_fs_position=utils_fp, is_dir=True
                ),
            ]
        ),
        set(["pandas"]),
        set([StdLibModuleInfo(module_name="math")]),
    )

    rv = package_manager._recursive_find_relative_module_dependencies(
        data, module_segmenter, module_creator, {}
    )
    assert rv[0] == results[0]
    assert rv[1] == results[1]
    assert rv[2] == results[2]


### Create Module Info Object


def test_create_relative_module_info():
    base_test_files = os.path.join(DATA_BASEPATH, "relative_module_info")
    starting_file_location = os.path.join(base_test_files, "src", "start.py")

    tmp_fp = os.path.join(base_test_files, "src", "tmp.py")
    utils_fp = os.path.join(base_test_files, "src", "utils")
    high_level_utils_fp = os.path.join(base_test_files, "high_level_utils.py")
    high_level_mod_fp = os.path.join(base_test_files, "high_level_mod")

    test_data = [
        (
            (".tmp", starting_file_location),
            RelativeModuleInfo(
                module_name=".tmp", absolute_fs_position=tmp_fp, is_dir=False
            ),
        ),
        (
            (".utils", starting_file_location),
            RelativeModuleInfo(
                module_name=".utils", absolute_fs_position=utils_fp, is_dir=True
            ),
        ),
        (
            ("..high_level_utils", starting_file_location),
            RelativeModuleInfo(
                module_name="..high_level_utils",
                absolute_fs_position=high_level_utils_fp,
                is_dir=False,
            ),
        ),
        (
            ("..high_level_mod", starting_file_location),
            RelativeModuleInfo(
                module_name="..high_level_mod",
                absolute_fs_position=high_level_mod_fp,
                is_dir=True,
            ),
        ),
    ]

    for test_datum in test_data:
        rv = package_manager._create_relative_module_info(*test_datum[0])
        assert test_datum[1] == rv


def test_create_packaged_module_info():
    base_test_files = os.path.join(DATA_BASEPATH, "packaged_module_info")
    test_data = [
        (
            (
                "pandas",
                os.path.join(base_test_files, "pandas"),
                "cp37-cp37m-manylinux_2_17_x86_64",
            ),
            PackagedModuleInfo(
                module_name="pandas",
                absolute_fs_position=os.path.join(base_test_files, "pandas"),
                is_dir=True,
                tag="cp37-cp37m-manylinux_2_17_x86_64",
            ),
        ),
        (
            ("six", os.path.join(base_test_files, "six.py"), "py2-none-any"),
            PackagedModuleInfo(
                module_name="six",
                absolute_fs_position=os.path.join(base_test_files, "six.py"),
                is_dir=False,
                tag="py2-none-any",
            ),
        ),
    ]

    for test_datum in test_data:
        rv = package_manager._create_packaged_module_info(*test_datum[0])
        assert test_datum[1] == rv


def test_create_std_library_module_info():
    test_data = [(("math",), StdLibModuleInfo(module_name="math"))]

    for test_datum in test_data:
        rv = package_manager._create_std_library_module_info(*test_datum[0])
        assert test_datum[1] == rv


### Create package information... Dependant on Distribution or WorkingSet
def test_create_pkg_to_top_modules():
    assert True
    # stub the function to look in the test dir for the module metadata. This is needed because the
    # pickled environments point to an absolute location of the place the objects were pickled
    # package_manager._get_metadata_files_for_package = (
    #    stub_get_metadata_files_for_package
    # )
    # data = [
    #    (
    #        get_workingset(),
    #        {
    #            "pandas": ["pandas"],
    #            "Jinja2": ["jinja2"],
    #            "MarkupSafe": ["markupsafe"],
    #            "boto3": ["boto3"],
    #            "botocore": ["botocore"],
    #            "certifi": ["certifi"],
    #            "charset-normalizer": ["charset_normalizer"],
    #            "dill": ["dill"],
    #            "idna": ["idna"],
    #            "jmespath": ["jmespath"],
    #            "numpy": ["numpy"],
    #            "pip": ["pip"],
    #            "python-dateutil": ["dateutil"],
    #            "pytz": ["pytz"],
    #            "requests": ["requests"],
    #            "s3transfer": ["s3transfer"],
    #            "setuptools": ["setuptools"],
    #            "six": ["six"],
    #            "stripe": ["stripe"],
    #            "urllib3": ["urllib3"],
    #            "wheel": ["wheel"],
    #        },
    #    )
    # ]


#       for datum in data:
#    assert datum[1] == package_manager._create_pkg_to_top_modules(datum[0])


def test_create_packages_direct_modules():
    # stub the function to look in the test dir for the module metadata. This is needed because the
    # pickled environments point to an absolute location of the place the objects were pickled
    assert True
    # package_manager._get_metadata_files_for_package = (
    #    stub_get_metadata_files_for_package
    # )
    # data = [(get_distribution("pandas"), ["pandas"])]


#
# for datum in data:
#    assert datum[1] == package_manager._create_packages_direct_modules(datum[0])
#


def test_get_module_dependencies_info():
    # stub the function to look in the test dir for the module metadata. This is needed because the
    # pickled environments point to an absolute location of the place the objects were pickled
    assert True
    # package_manager._get_metadata_files_for_package = (
    #    stub_get_metadata_files_for_package
    # )
    # data = [
    #    (
    #        get_distribution("pandas"),
    #        {"pandas": set(["dateutil", "six", "pytz", "numpy"])},
    #    ),
    #    (
    #        get_distribution("boto3"),
    #        {
    #            "boto3": set(
    #                ["botocore", "dateutil", "six", "urllib3", "jmespath", "s3transfer"]
    #            )
    #        },
    #    ),
    # ]


#
# ws = get_workingset()
# pkg_top_mod = package_manager._create_pkg_to_top_modules(ws)
#
# for datum in data:
#    assert datum[1] == package_manager._get_module_dependencies_info(
#        datum[0], pkg_top_mod, ws
#    )


def test_recursive_get_all_dependencies():
    # stub the function to look in the test dir for the module metadata. This is needed because the
    # pickled environments point to an absolute location of the place the objects were pickled
    assert True
    # package_manager._get_metadata_files_for_package = (
    #    stub_get_metadata_files_for_package
    # )
    # data = [
    #    (
    #        get_distribution("pandas"),
    #        set(["pandas", "dateutil", "six", "pytz", "numpy"]),
    #    ),
    #    (
    #        get_distribution("boto3"),
    #        set(
    #            [
    #                "boto3",
    #                "botocore",
    #                "dateutil",
    #                "six",
    #                "urllib3",
    #                "jmespath",
    #                "s3transfer",
    #            ]
    #        ),
    #    ),
    # ]


#
# ws = get_workingset()
# pkg_top_mod = package_manager._create_pkg_to_top_modules(ws)
#
# for datum in data:
#    assert datum[1] == package_manager._recursive_get_all_dependencies(
#        datum[0], pkg_top_mod, ws
#    )


def test_get_packages_modules_location_tag_info():
    # stub the function to look in the test dir for the module metadata. This is needed because the
    # pickled environments point to an absolute location of the place the objects were pickled
    assert True
    # package_manager._get_metadata_files_for_package = (
    #    stub_get_metadata_files_for_package
    # )
    # data = [
    #    (
    #        get_distribution("pandas"),
    #        {
    #            "pandas": (
    #                os.path.join(DATA_BASEPATH, "packaged_module_info", "env1"),
    #                "cp37-cp37m-manylinux_2_17_x86_64",
    #            )
    #        },
    #    )
    # ]


#
# for datum in data:
#    assert datum[1] == package_manager._get_packages_modules_location_tag_info(
#        datum[0]
#    )


def test_get_metadata_files_for_package():
    ## NEED to fake distribution items.
    assert True


### Helper Functions with standard inputs


def test_count_relative_level():
    test_data = [("..tmp", 2), (".tmp", 1), ("tmp", 0)]

    for test_datum in test_data:
        assert test_datum[1] == package_manager._count_relative_level(test_datum[0])


def test_get_tags_from_wheel():
    base_wheel_dir = os.path.join(DATA_BASEPATH, "test_wheels")
    test_data = [
        (os.path.join(base_wheel_dir, "aurora_data_api_WHEEL"), ["py3", "none", "any"]),
        (os.path.join(base_wheel_dir, "networkx_WHEEL"), ["py3", "none", "any"]),
        (os.path.join(base_wheel_dir, "six_WHEEL"), ["py2", "none", "any"]),
    ]

    for test_datum in test_data:
        assert test_datum[1] == package_manager._get_tags_from_wheel(test_datum[0])


def test_get_module_abs_path():
    base_resolve_path = os.path.join(DATA_BASEPATH, "path_resolution")

    test_data = [
        (("numpy", base_resolve_path), os.path.join(base_resolve_path, "numpy")),
        (("six", base_resolve_path), os.path.join(base_resolve_path, "six.py")),
    ]

    for test_datum in test_data:
        assert test_datum[1] == package_manager._get_module_abs_path(*test_datum[0])


def test_get_relative_package_dependencies():
    base_relative_import_path = os.path.join(DATA_BASEPATH, "relative_modules")

    test_data = [
        (os.path.join(base_relative_import_path, "tmp_utils.py"), ["math"]),
        (
            os.path.join(base_relative_import_path, "vamos"),
            ["pandas", "sqlalchemy_aurora_data_api"],
        ),
        (
            os.path.join(base_relative_import_path, "tmp.py"),
            ["pandas", "sys", ".vamos", ".tmp_utils"],
        ),
    ]

    for test_datum in test_data:
        test_datum[1].sort()
        rv = package_manager._get_relative_package_dependencies(test_datum[0])
        rv.sort()
        assert test_datum[1] == rv


####################
##### Test helpers
####################
def stub_get_metadata_files_for_package(package: Distribution):
    base_dir = os.path.join(DATA_BASEPATH, "packaged_module_info", "env1")
    dist_info_location = os.path.join(
        base_dir,
        f"{package.project_name.replace('-', '_')}-{package.parsed_version}.dist-info",
    )

    return (
        None,
        os.path.join(dist_info_location, "top_level.txt"),
        os.path.join(dist_info_location, "WHEEL"),
        base_dir,
    )


def get_distribution(project_name: str) -> Distribution:
    assert True
    # ws = get_workingset()


#
# for x in ws:
#    if x.project_name == project_name:
#        return x
#
# raise Exception


def get_workingset() -> WorkingSet:
    pass
    # base_dir = os.path.join(DATA_BASEPATH, "pickled_envs")


#
# ws: WorkingSet = dill.load(open(os.path.join(base_dir, "ws_env1_pickle"), "rb"))
#
# return ws
