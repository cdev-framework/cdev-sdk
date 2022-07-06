import os
from subprocess import run

from cdev.utils.git_safe.utils import get_repo


########################################
##### Exceptions
########################################
class MergeException(Exception):
    pass


class PullException(Exception):
    pass


# Merge the branch with no ff or commit
def merge_branch(branch_name: str) -> None:

    rv = run(["git", "merge", "--no-ff", "--no-commit", branch_name])

    if rv.returncode == 0:
        return

    raise MergeException(rv)


# Merge the branch with no ff or commit
def pull_branch(repository: str, ref_spec: str) -> None:

    rv = run(["git", "pull", "--no-ff", "--no-commit", repository, ref_spec])

    if rv.returncode == 0:
        return

    raise PullException(rv)


# RESET THE FILE
def clean_up_resource_states() -> None:
    pass
    # rv = run(
    #    [
    #        "git",
    #        "reset",
    #        "--",
    #        ".cdev/state/resource_state_b58a461b-ddb5-454f-9b71-bed695e38a37.json",
    #    ]
    # )


#
# if rv.returncode == 0:
#    rv2 = run(
#        [
#            "git",
#            "checkout",
#            "--",
#            ".cdev/state/resource_state_b58a461b-ddb5-454f-9b71-bed695e38a37.json",
#        ]
#    )
#    return
#
# raise Exception


# FINISH MERGE
def commit_merge(message: str) -> None:
    repo = get_repo(os.getcwd())
    repo.git.commit(f"-m {message}")


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
