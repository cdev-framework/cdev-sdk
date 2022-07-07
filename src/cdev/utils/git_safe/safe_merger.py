from dataclasses import dataclass
from email import message
import os
from subprocess import run

from cdev.utils.git_safe.utils import (
    get_repo,
    clean_up_resource_states_util,
    ProjectNotMerged,
    ProjectFileEdited,
    ProjectFileReadingError,
    PreserveResourceStatesError,
)


from cdev.utils.git_safe import safe_merger_error_messages

########################################
##### Exceptions
########################################
class MergeException(Exception):
    pass


class AbortMergeException(Exception):
    pass


class FetchException(Exception):
    pass


class CommitException(Exception):
    pass


@dataclass
class CleanUpResourceStateException(Exception):
    message: str


# Merge the branch with no ff or commit
def merge_branch(branch_name: str) -> None:

    rv = run(["git", "merge", "--no-ff", "--no-commit", branch_name])

    if rv.returncode == 0:
        return

    raise MergeException(rv)


# Abort the current merge
def abort_merge() -> None:

    rv = run(["git", "merge", "--abort"])

    if rv.returncode == 0:
        return

    raise AbortMergeException(rv)


# Merge the branch with no ff or commit
def pull_branch(repository: str, ref_spec: str) -> None:
    fetch_remote(repository)
    merge_branch(f"{repository}/{ref_spec}")


def fetch_remote(repository: str) -> None:
    rv = run(["git", "fetch", repository])

    if rv.returncode == 0:
        return

    raise FetchException(rv)


# RESET THE FILE
def clean_up_resource_states() -> None:
    try:
        clean_up_resource_states_util()
    except ProjectNotMerged as e:
        raise CleanUpResourceStateException(
            message=safe_merger_error_messages.project_not_merged
        )
    except ProjectFileEdited as e:
        raise CleanUpResourceStateException(
            message=safe_merger_error_messages.project_file_edited
        )
    except ProjectFileReadingError as e:
        raise CleanUpResourceStateException(
            message=safe_merger_error_messages.project_file_reading
        )
    except PreserveResourceStatesError as e:
        raise CleanUpResourceStateException(
            message=safe_merger_error_messages.preserve_resource_states
        )


# FINISH MERGE
def commit_merge(message: str) -> None:
    repo = get_repo(os.getcwd())
    try:
        repo.git.commit(f"-m {message}")
    except Exception as e:
        print(e)
        raise CommitException


# try:
#    merge_branch('cdev-branch-1')
# except Exception as e:
#    print(e)
#    exit(0)
# try:
#    clean_up_resource_states()
# except Exception as e:
#    print(e)
#    exit(0)
#
# try:
#    commit_merge("CDEV SAFE MERGE")
#    print('##################################')
#    print('SUCCESSFULLY MERGED ')
#    print('##################################')
# except Exception as e:
#    print(e)
#    exit(0)
