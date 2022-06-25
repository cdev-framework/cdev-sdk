from typing import Optional
import os

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError

from pydantic import DirectoryPath


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
