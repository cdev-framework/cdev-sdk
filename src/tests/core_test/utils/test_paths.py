import os

from core.utils import paths
from core.constructs.settings import Settings
from core.constructs.workspace import Workspace

tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")


settings = Settings()
settings.BASE_PATH = tmp_dir
settings.INTERMEDIATE_FOLDER_LOCATION = tmp_dir


ws = Workspace()
ws.settings = settings

# monkey patch the global workspace
Workspace.set_global_instance(ws)


def test_get_relative_to_workspace_path():
    full_path = os.path.join(tmp_dir, "hey", "world")
    assert paths.get_relative_to_workspace_path(full_path) == "hey/world"


def test_get_relative_to_intermediate_path():
    full_path = os.path.join(tmp_dir, "hey", "world")
    assert paths.get_relative_to_intermediate_path(full_path) == "hey/world"


def test_get_full_path_from_workspace_base():
    full_path = os.path.join(tmp_dir, "hey", "world")
    assert paths.get_full_path_from_workspace_base("hey/world") == full_path


def test_get_full_path_from_intermediate_base():
    full_path = os.path.join(tmp_dir, "hey", "world")
    assert paths.get_full_path_from_intermediate_base("hey/world") == full_path


def test_is_in_workspace():
    full_path = os.path.join(tmp_dir, "hey", "world")

    assert paths.is_in_workspace(full_path)
    assert not paths.is_in_workspace(__file__)


def test_is_in_intermediate():
    full_path = os.path.join(tmp_dir, "hey", "world")
    print(Workspace.instance().settings.INTERMEDIATE_FOLDER_LOCATION)
    print(full_path)
    assert paths.is_in_intermediate(full_path)
    # assert not paths.is_in_workspace(__file__)


def test_get_workspace_path():
    assert paths.get_workspace_path() == settings.BASE_PATH


def test_get_intermediate_path():
    assert paths.get_intermediate_path() == settings.INTERMEDIATE_FOLDER_LOCATION


def test_create_path():

    dirs = ["testp1", "testp2", "testp3"]

    paths.create_path(tmp_dir, dirs)

    tmp = tmp_dir

    for x in dirs:
        tmp = os.path.join(tmp, x)

        assert os.path.isdir(tmp)
