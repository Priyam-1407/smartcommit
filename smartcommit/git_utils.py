"""
All Git interactions live here. Nothing else in the codebase should
call GitPython directly -- keeps Git logic testable and isolated.
"""

from git import Repo, InvalidGitRepositoryError
from git.exc import GitCommandError


class NotAGitRepoError(Exception):
    pass


class NoStagedChangesError(Exception):
    pass


def get_repo(path: str = ".") -> Repo:
    """Return the Git repo object for the given path, or raise if not a repo."""
    try:
        return Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise NotAGitRepoError(
            "Not a git repository. Run this inside a folder with `git init` "
            "or a cloned repo."
        )


def get_staged_diff(repo: Repo) -> str:
    """
    Returns the diff of staged changes (i.e. what `git diff --staged` shows).
    Raises NoStagedChangesError if nothing is staged.
    """
    diff = repo.git.diff("--staged")
    if not diff.strip():
        raise NoStagedChangesError(
            "No staged changes found. Run `git add <files>` first."
        )
    return diff


def get_changed_file_names(repo: Repo) -> list[str]:
    """Returns list of file paths that are staged for commit."""
    diff_index = repo.index.diff("HEAD")
    return [item.a_path for item in diff_index]


def commit(repo: Repo, message: str) -> str:
    """
    Commits staged changes with the given message.
    Returns the commit hash.
    """
    try:
        commit_obj = repo.index.commit(message)
        return commit_obj.hexsha[:7]
    except GitCommandError as e:
        raise RuntimeError(f"Git commit failed: {e}")
