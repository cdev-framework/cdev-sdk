# cdev git-safe merge <branch/id> --abort --continue

# git merge --no-ff --no-commit <>

# if no conflicts:
#   - <resolve_environments>

# if conflicts:
#   - resolve conflicts
#   - must rerun with --continue -> <resolve_environments>

# resolve environments:
#   - read the project state then preserve any resource states
from argparse import Namespace
import json
import os

from pydantic import FilePath

from cdev.default.project import local_project_info

from cdev.utils.git_safe.merger_installer import install_custom_merger
from cdev.utils.git_safe.project_merger import (
    merge_local_project_info,
    RichDifferenceHelper,
    ExitedMerge,
)
from cdev.utils.git_safe.safe_merger import (
    merge_branch,
    clean_up_resource_states,
    commit_merge,
    abort_merge,
    pull_branch,
    MergeException,
    AbortMergeException,
    FetchException,
    CommitException,
    CleanUpResourceStateException,
)

from cdev.commands import git_safe_messages

from core.utils.file_manager import safe_json_write


def git_safe_cli(
    command: str,
    parsed_args_namespace: Namespace,
    **kwargs,
) -> None:

    parsed_args = vars(parsed_args_namespace)

    if command == "":
        print(git_safe_messages.no_command_message)
    elif command == "install-merger":
        git_safe_install_merger(**parsed_args)
    elif command == "pull":
        git_safe_pull(**parsed_args)
    elif command == "merge":
        git_safe_merge(**parsed_args)
    elif command == "project-merger":
        git_custom_project_merger(**parsed_args)
    else:
        print("BAD COMMAND")


def git_safe_install_merger(**kwargs) -> None:
    install_custom_merger(os.getcwd())
    print("-----Installed Cdev Customer Merger Utility-----")


def git_safe_pull(repository: str, ref_spec: str, **kwargs) -> None:

    try:
        pull_branch(repository, ref_spec)
    except FetchException:
        print(git_safe_messages.failed_fetch_message)
        return
    except MergeException:
        print(git_safe_messages.failed_merge_message)
        return

    try:
        clean_up_resource_states()
    except CleanUpResourceStateException as e:
        print(e.message)
        return

    try:
        commit_merge("CDEV SAFE MERGE")
    except CommitException:
        print(git_safe_messages.failed_commit_message)

    print(git_safe_messages.success_pull_message)


def git_safe_merge(commit: str = None, abort: bool = None, **kwargs):
    _continue = kwargs.get("continue")

    _opt_params_list = [abort, _continue]

    if not any(_opt_params_list + [commit]):
        print(f"ERROR: Can must provide one of <commit>, --continue, --abort")
        return

    if len([x for x in _opt_params_list + [commit] if x]) > 1:
        print(f"ERROR: Can only use one of <commit>, --continue, --abort at a time")
        return

    if commit:
        try:
            merge_branch(commit)
        except MergeException:
            print(git_safe_messages.failed_merge_message)
            return

        try:
            clean_up_resource_states()
        except CleanUpResourceStateException as e:
            print(e.message)
            return

        try:
            commit_merge("CDEV SAFE MERGE")
        except CommitException:
            print(git_safe_messages.failed_commit_message)

        print(git_safe_messages.success_merge_message)

    elif _continue:
        try:
            clean_up_resource_states()
        except CleanUpResourceStateException as e:
            print(e.message)
            return

        try:
            commit_merge("CDEV SAFE MERGE")
        except CommitException:
            print(git_safe_messages.failed_commit_message)
            return

        print(git_safe_messages.success_merge_message)

    elif abort:
        try:
            abort_merge()
            print(git_safe_messages.success_merge_abort_message)
        except AbortMergeException:
            print(git_safe_messages.failed_abort_merge_message)
            return


def git_custom_project_merger(
    current_fp: FilePath, other_fp: FilePath, **kwargs
) -> None:

    try:
        other_project_info = _load_local_project_information(other_fp)
    except Exception:
        print(git_safe_messages.failed_to_load_other_message)
        exit(1)

    try:
        current_project_info = _load_local_project_information(current_fp)
    except Exception:
        print(git_safe_messages.failed_to_load_current_message)
        exit(1)

    try:
        merged_info = merge_local_project_info(
            other_project_info, current_project_info, RichDifferenceHelper()
        )
    except ExitedMerge:
        print(git_safe_messages.exited_merge_message)
        exit(1)

    safe_json_write(merged_info.dict(), current_fp)

    exit(0)


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
