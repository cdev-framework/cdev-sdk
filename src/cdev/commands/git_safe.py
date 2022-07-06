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
from re import L

from pydantic import FilePath

from cdev.default.project import local_project_info

from cdev.utils.git_safe.merger_installer import install_custom_merger
from cdev.utils.git_safe.project_merger import (
    merge_local_project_info,
    RichDifferenceHelper,
)
from cdev.utils.git_safe.safe_merger import (
    merge_branch,
    clean_up_resource_states,
    commit_merge,
    pull_branch,
    MergeException,
    PullException,
)

from core.utils.file_manager import safe_json_write


def git_safe_cli(
    command: str,
    parsed_args_namespace: Namespace,
    **kwargs,
) -> None:

    parsed_args = vars(parsed_args_namespace)

    if command == "":
        print("NEED TO SUPPLY A COMMAND")
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
    print("INSTALL")
    install_custom_merger(os.getcwd())


def git_safe_pull(repository: str, ref_spec: str, **kwargs) -> None:
    if repository and ref_spec:
        pull_branch(repository, ref_spec)

        clean_up_resource_states()
        print("fix resource states")
        commit_merge("CDEV SAFE MERGE")
        print("commited")


def git_safe_merge(commit: str = None, abort: bool = None, quit: bool = None, **kwargs):
    _continue = kwargs.get("continue")

    _opt_params_list = [abort, _continue, quit]

    if not any(_opt_params_list + [commit]):
        print(f"ERROR: Can must provide one of <commit>, --continue, --abort, --quit")
        return

    if commit and any(_opt_params_list):
        print(
            f"ERROR: Can not use --continue, --abort, --quit with the <commit> positional argument"
        )
        return

    if len([x for x in _opt_params_list if x]) > 1:
        print(f"ERROR: Can only use one of --continue, --abort, --quit at a time")
        return

    if commit:
        try:
            merge_branch(commit)
        except MergeException:
            print(_failed_merge_message)
            return

        clean_up_resource_states()

        commit_merge("CDEV SAFE MERGE")


def git_custom_project_merger(
    current_fp: FilePath, other_fp: FilePath, **kwargs
) -> None:
    print("CURRENT")
    # current_fp = sys.argv[2]
    print(os.path.isfile(current_fp))
    # print(open(sys.argv[2]).read())

    print("OTHER")
    # other_fp = sys.argv[3]
    print(os.path.isfile(other_fp))
    # print(open(sys.argv[3]).read())

    other_project_info = _load_local_project_information(other_fp)
    current_project_info = _load_local_project_information(current_fp)

    merged_info = merge_local_project_info(
        other_project_info, current_project_info, RichDifferenceHelper()
    )

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


#############################################
##### Help Messages
#############################################

_failed_merge_message = """
+++++++++++++++MERGE FAILED+++++++++++++++++

Cdev safe-git was not able to automatically merge the commits. Above are the errors raised by git for the merge. You will need to manually fix the failed files and finish the merge, or you can abandon the merge:

<Manually fix file>
git add <files>
cdev git-safe merge --continue

or

cdev git-safe merge --abort

or

cdev git-safe merge --quit

++++++++++++++++++++++++++++++++++++++++++++
"""
