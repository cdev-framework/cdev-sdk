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
    else:
        print("BAD COMMAND")


def git_safe_install_merger(**kwargs) -> None:
    print("INSTALL")


def git_safe_pull(**kwargs) -> None:
    print("PULL")


def git_safe_merge(**kwargs):
    print(kwargs)
    print("MERGE")
