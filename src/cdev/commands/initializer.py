import json
import os
from pydantic import FilePath
from pydantic.types import DirectoryPath
import shutil
from typing import Dict, Tuple, List

from rich.prompt import Prompt
from cdev.default.project import local_project
from cdev.cli.logger import set_global_logger_from_cli

from core.constructs.backend import Backend, Backend_Configuration
from core.constructs.workspace import Workspace_Info
from core.default.backend import Local_Backend_Configuration, LocalBackend


from ..constructs.project import Project_State, check_if_project_exists, project_info


STATE_FOLDER = "state"
INTERMEDIATE_FOLDER = "intermediate"
CACHE_FOLDER = "cache"
CDEV_FOLDER = ".cdev"
CDEV_PROJECT_FILE = "cdev_project.json"
CENTRAL_STATE_FILE = "central_state.json"
SETTINGS_FOLDER_NAME = "settings"
DEFAULT_ENVIRONMENTS = ["prod", "stage", "dev"]
TEMPLATE_LOCATIONS = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "project_templates"
)

AVAILABLE_TEMPLATES = [
    "quick-start",
    "quick-start-twilio",
    "resources-test",
    "packages",
    "slack-bot",
    "user-auth",
    "power-tools",
]


def create_project_cli(args) -> None:
    """CLI version of the create project command.

    Args:
        args (_type_): cli arguments
    """
    config = args
    set_global_logger_from_cli(config.loglevel)

    create_project(args.name)

    if args.template:
        template_name = args.template

        if template_name not in AVAILABLE_TEMPLATES:
            print(
                f"{template_name} is not one of the available templates. {AVAILABLE_TEMPLATES}"
            )
            return

        print(f"Loading Template {template_name}")
        _load_template(template_name)
        print(f"Created Project From Template: {template_name}")


def _load_template(template_name: str, base_directory: DirectoryPath = None) -> None:
    """Copy the given template name into the provided directory.

    Args:
        template_name (str): Name of the template
        base_directory (DirectoryPath): directory to copy to. defaults to os.cwd().
    """
    if not base_directory:
        base_directory = os.getcwd()

    template_folder_name = template_name.replace("-", "_")

    if not template_folder_name in os.listdir(TEMPLATE_LOCATIONS):
        print(f"Could not finder template for {template_folder_name}")
        return

    template_location = os.path.join(TEMPLATE_LOCATIONS, template_folder_name)
    for x in os.listdir(template_location):

        full_location = os.path.join(template_location, x)
        if os.path.isdir(full_location):
            shutil.copytree(full_location, os.path.join(base_directory, x))
        elif os.path.isfile(full_location):
            shutil.copyfile(full_location, os.path.join(base_directory, x))


def create_project(project_name: str, base_directory: DirectoryPath = None) -> None:
    """Create a new `Project` at the given base_directory (or cwd). This initializes all the files needed
    to create a basic Cdev Project.

    Args:
        project_name (str): name of the project
        base_directory (DirectoryPath, optional): directory to store information. Defaults to cwd().

    Raises:
        Exception: If a Cdev project already exists at the given location.
    """

    if not base_directory:
        base_directory = os.getcwd()

    if check_if_project_exists(base_directory):
        raise Exception("Project Already Created")

    base_settings_values = _default_new_project_input_questions()
    _create_folder_structure(
        base_directory,
        base_settings=base_settings_values,
        extra_environments=DEFAULT_ENVIRONMENTS,
    )

    base_settings_folder = os.path.join(base_directory, SETTINGS_FOLDER_NAME)

    backend_directory = os.path.join(base_directory, CDEV_FOLDER, STATE_FOLDER)
    backend_configuration = Local_Backend_Configuration(
        {
            "base_folder": backend_directory,
            "central_state_file": os.path.join(backend_directory, CENTRAL_STATE_FILE),
        }
    )

    new_project_info = project_info(
        project_name,
        environments=[],
        backend_info=backend_configuration,
        current_environment="",
    )

    project_info_location = os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)
    with open(project_info_location, "w") as fh:
        json.dump(new_project_info.dict(), fh, indent=4)

    new_project = local_project(project_info_location)

    new_project.initialize_project()

    # TODO restructure entire creating process so that this is more explicit
    base_dir = os.getcwd()

    for environment in DEFAULT_ENVIRONMENTS:

        environment_settings = {
            "user_setting_module": [
                # set the settings modules as python modules
                os.path.relpath(
                    os.path.join(base_settings_folder, f"base_settings.py"),
                    start=base_dir,
                )[:-3].replace("/", "."),
                os.path.relpath(
                    os.path.join(base_settings_folder, f"{environment}_settings.py"),
                    start=base_dir,
                )[:-3].replace("/", "."),
            ],
            "secret_dir": os.path.relpath(
                os.path.join(base_settings_folder, f"{environment}_secrets"),
                start=base_dir,
            ),
        }

        new_project.create_environment(environment, environment_settings)

    new_project.set_state(Project_State.UNINITIALIZED)

    new_project.set_current_environment(DEFAULT_ENVIRONMENTS[-1])


def _default_new_project_input_questions() -> Dict[str, str]:
    """Run through the sequence of input questions for a user to properly initialize a project.

    Returns:
        Dict[str, str]: Settings completed by the user
    """
    rv = {}

    _artifact_bucket = Prompt.ask(
        prompt="Name of bucket to store artifacts", default=""
    )

    rv = {"S3_ARTIFACTS_BUCKET": _artifact_bucket}

    return rv


def _create_folder_structure(
    base_directory: DirectoryPath,
    base_settings: Dict[str, str] = None,
    extra_environments: List[str] = None,
) -> None:
    """Create a skeleton file structure needed to make a project and additional environments. Apply the Dict of base settings to the generated
    base settings file.

    Args:
        base_directory (DirectoryPath)
        base_settings (Dict[str, str], optional): Settings for base environment. Defaults to None.
        extra_environments (List[str], optional): List of environments to generate. Defaults to None.
    """
    cdev_folder = os.path.join(base_directory, CDEV_FOLDER)
    state_folder = os.path.join(cdev_folder, STATE_FOLDER)
    intermediate_folder = os.path.join(cdev_folder, INTERMEDIATE_FOLDER)
    cache_folder = os.path.join(intermediate_folder, CACHE_FOLDER)
    settings_folder = os.path.join(base_directory, SETTINGS_FOLDER_NAME)
    base_settings_file = os.path.join(settings_folder, f"base_settings.py")

    _mkdir(cdev_folder)
    _mkdir(state_folder)
    _mkdir(intermediate_folder)
    _mkdir(cache_folder)
    _mkdir(settings_folder)

    _create_base_settings(base_settings_file, base_settings)

    for environment in extra_environments:
        _touch_file(os.path.join(settings_folder, f"{environment}_settings.py"))
        _mkdir(os.path.join(settings_folder, f"{environment}_secrets"))


def _create_base_settings(
    file_path: FilePath, base_settings: Dict[str, str] = None
) -> None:
    """Create the base settings for the project at the provide path. This creates a python module at the provided directory, creates
    a base settings file, and applies any base settings to the generate file.

    Args:
        file_path (FilePath): path of the file
        base_settings (Dict[str, str], optional): Settings for base environment. Defaults to None.
    """
    # The settings are dynamically importable python modules, so the folder needs to be a python module
    _touch_file(os.path.join(os.path.dirname(file_path), f"__init__.py"))

    _touch_file(file_path)

    if base_settings:
        _render_settings_file(file_path, base_settings)


def _render_settings_file(file_path: FilePath, base_settings: Dict[str, str]) -> None:
    """Apply the base settings to the given file

    Args:
        file_path (FilePath): path of the file
        base_settings (Dict[str, str]): settings to apply
    """
    with open(file_path, "w") as fh:
        for key, value in base_settings.items():
            fh.write(f'{key} = "{value}"')


def _touch_file(file_path: FilePath) -> None:
    """Helper function to touch a file

    Args:
        file_path (FilePath)

    Raises:
        Exception: Directory does not exist
    """
    if not os.path.isdir(os.path.dirname(file_path)):
        raise Exception(
            f"Can not create {file_path} because {os.path.dirname(file_path)} is not a directory."
        )

    with open(file_path, "w"):
        pass


def _mkdir(directory_path: DirectoryPath) -> None:
    """Create a directory if it does not already exist.

    Args:
        directory_path (DirectoryPath)
    """
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)


def load_project(initialize: bool = False) -> None:
    """Create the global instance of the `Project` object. If provided, also initialize the `Project`.

    Args:
        initialize (bool, optional): Defaults to False.
    """
    base_directory = os.getcwd()

    project_info_location = os.path.join(base_directory, CDEV_FOLDER, CDEV_PROJECT_FILE)

    local_project(project_info_location) if not initialize else local_project(
        project_info_location
    ).initialize_project()
