from enum import Enum
import json
from typing import Optional, Dict, List
import os

import git
from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError

from pydantic import DirectoryPath, FilePath

from cdev.default.project import local_project_info


########################################
##### Exceptions
########################################
class ProjectNotMerged(Exception):
    pass


class ProjectFileEdited(Exception):
    pass


class ProjectFileReadingError(Exception):
    pass


class PreserveResourceStatesError(Exception):
    pass


########################################
##### Global Config and Enums
########################################

CDEV_PROJECT_FILE_LOCATION = ".cdev/cdev_project.json"


class GitMergeFileStates(str, Enum):
    UNMERGED = "UNMERGED"
    MODIFIED = "MODIFIED"
    ADD = "ADD"
    DELETE = "DELETED"
    RENAMED = "RENAMED"


_change_str_to_GMFS = {
    "U": GitMergeFileStates.UNMERGED,
    "M": GitMergeFileStates.MODIFIED,
    "A": GitMergeFileStates.ADD,
    "D": GitMergeFileStates.DELETE,
}


########################################
##### Apis
########################################


def get_repo(dir: DirectoryPath) -> Optional[Repo]:
    _git_dir = os.path.join(dir, ".git")
    if is_repo(_git_dir):
        return Repo(_git_dir)

    return None


def is_repo(dir: DirectoryPath) -> bool:
    try:
        _ = Repo(dir).git_dir
        return True
    except InvalidGitRepositoryError:
        return False
    except NoSuchPathError:
        return False
    except Exception:
        return False


def create_repo(dir: DirectoryPath) -> Repo:
    return Repo.init(dir)


def clean_up_resource_states_util() -> None:
    repo = Repo()
    staged_files = repo.index.diff("HEAD")
    working_directory_files = repo.index.diff(None)

    if not staged_files:
        # This is a best effort fix any mistakes with deleting resource states, so if we are not it the correct place within the context
        # of git, then we can just pass through and let a downstream process decide what to do
        return

    _staged_files_information = _reverse_deletes_adds(_process_git_diff(staged_files))
    _working_directory_files_information = _process_git_diff(working_directory_files)

    if (
        CDEV_PROJECT_FILE_LOCATION in _staged_files_information
        and _staged_files_information.get(CDEV_PROJECT_FILE_LOCATION)
        == GitMergeFileStates.UNMERGED
    ):
        # If the project state has not been cleaned up (fixed merge conflicts) and staged, we should not proceed because it could be in a bad state
        raise ProjectNotMerged

    if CDEV_PROJECT_FILE_LOCATION in _working_directory_files_information:
        # if the project state is staged but the working directory has a changes on it, then it is potentially not safe to read
        raise ProjectFileEdited

    try:
        staged_project_info = _load_local_project_information(
            CDEV_PROJECT_FILE_LOCATION
        )
    except Exception:
        # If we can not read the working directory cdev project file and it is the same as the staged version, then we should not proceed.
        raise ProjectFileReadingError

    _resource_states_to_preserve = _compute_cleanup_resource_state_actions(
        staged_project_info, _staged_files_information
    )

    if _resource_states_to_preserve:
        try:
            repo.index.reset("HEAD", paths=_resource_states_to_preserve)
            repo.index.checkout(paths=_resource_states_to_preserve)
        except Exception:
            raise PreserveResourceStatesError


# duplicate from __main__.py, will refactor to a central location
def _load_local_project_information(
    project_info_location: FilePath,
) -> local_project_info:
    """Help function to load the project info json file

    Args:
        project_info_location (FilePath): location of project info json

    Returns:
        local_project_info
    """
    with open(project_info_location, "r") as fh:
        json_information = json.load(fh)

        local_project_info_model = local_project_info(**json_information)

    return local_project_info_model


def _process_git_diff(staged_files: git.DiffIndex) -> Dict[str, GitMergeFileStates]:
    return {
        x.b_path: _change_str_to_GMFS.get(x.change_type)
        if not x.renamed_file
        else GitMergeFileStates.RENAMED
        for x in staged_files
    }


def _compute_resource_state_file_location(resource_state_uuid: str) -> str:
    return os.path.join(".cdev", "state", f"resource_state_{resource_state_uuid}.json")


def _compute_cleanup_resource_state_actions(
    project_info: local_project_info, file_diffs: Dict[str, GitMergeFileStates]
):
    rv = []

    for environment in project_info.environment_infos:
        _rs_file_location = _compute_resource_state_file_location(
            environment.workspace_info.resource_state_uuid
        )

        if (
            _rs_file_location in file_diffs
            and file_diffs.get(_rs_file_location) == GitMergeFileStates.DELETE
        ):
            rv.append(_rs_file_location)

    return rv


def _reverse_deletes_adds(
    file_diffs: Dict[str, GitMergeFileStates]
) -> Dict[str, GitMergeFileStates]:
    _map = {
        GitMergeFileStates.UNMERGED: GitMergeFileStates.UNMERGED,
        GitMergeFileStates.MODIFIED: GitMergeFileStates.MODIFIED,
        GitMergeFileStates.RENAMED: GitMergeFileStates.RENAMED,
        GitMergeFileStates.ADD: GitMergeFileStates.DELETE,
        GitMergeFileStates.DELETE: GitMergeFileStates.ADD,
    }

    return {k: _map.get(v) for k, v in file_diffs.items()}
