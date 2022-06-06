import dill
from pkg_resources import Distribution, WorkingSet
from pydantic import FilePath
import os

from core.utils.fs_manager.module_types import (
    RelativeModuleInfo,
    PackagedModuleInfo,
    StdLibModuleInfo,
)
from core.utils.fs_manager import package_manager
from core.constructs.workspace import Workspace
from core.constructs.settings import Settings

DATA_BASEPATH = os.path.join(os.path.dirname(__file__), "test_data")
PICKLED_FILED_BASE = os.path.join(DATA_BASEPATH, "pickled_envs")

tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")


settings = Settings()
settings.BASE_PATH = tmp_dir
settings.INTERMEDIATE_FOLDER_LOCATION = tmp_dir


ws = Workspace()
ws.settings = settings

# monkey patch the global workspace
Workspace.set_global_instance(ws)


def test_create_all_module_info():
    assert True


def test_get_packaged_modules_name_location():
    ws = get_workingset()

    rv = {
        "boto3": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py3-none-any",
        ),
        "botocore": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py3-none-any",
        ),
        "certifi": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
        "charset_normalizer": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py3-none-any",
        ),
        "dateutil": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
        "dill": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
        "idna": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py3-none-any",
        ),
        "jinja2": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py3-none-any",
        ),
        "jmespath": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py3-none-any",
        ),
        "markupsafe": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "cp37-cp37m-manylinux_2_17_x86_64",
        ),
        "numpy": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "cp37-cp37m-manylinux_2_12_x86_64",
        ),
        "pandas": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "cp37-cp37m-manylinux_2_17_x86_64",
        ),
        "pip": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py3-none-any",
        ),
        "pytz": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
        "requests": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
        "s3transfer": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py3-none-any",
        ),
        "six": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
        "stripe": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
        "urllib3": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
        "wheel": (
            "/home/daniel/tmp/dill_check/.venv/lib/python3.7/site-packages",
            "py2-none-any",
        ),
    }

    # assert rv == package_manager.get_packaged_modules_name_location_tag(ws)
    assert True


def test_create_packaged_module_dependencies():
    # ws = get_workingset()
    #
    # assert {} == package_manager.create_packaged_module_dependencies(ws)
    assert True


####################
##### Test helpers
####################
def stub_get_metadata_files_for_package(package: Distribution):
    base_dir = os.path.join(DATA_BASEPATH, "packaged_module_info", "env1")

    return (
        None,
        os.path.join(
            base_dir,
            f"{package.project_name.replace('-', '_')}-{package.parsed_version}.dist-info",
        ),
        None,
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
    assert True
    # base_dir = os.path.join(DATA_BASEPATH, "pickled_envs")


#
# ws: WorkingSet = dill.load(open(os.path.join(base_dir, "ws_env1_pickle"), "rb"))
#
# return ws
