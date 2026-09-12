import pytest
from git import Repo

from smartcommit.git_utils import (
    get_staged_diff,
    get_changed_file_names,
    commit,
    NoStagedChangesError,
)


@pytest.fixture
def temp_repo(tmp_path):
    repo = Repo.init(tmp_path)
    # initial commit so we have a HEAD to diff against
    f = tmp_path / "readme.txt"
    f.write_text("hello\n")
    repo.index.add(["readme.txt"])
    repo.index.commit("initial commit")
    return repo, tmp_path


def test_no_staged_changes_raises(temp_repo):
    repo, _ = temp_repo
    with pytest.raises(NoStagedChangesError):
        get_staged_diff(repo)


def test_staged_diff_detected(temp_repo):
    repo, path = temp_repo
    f = path / "readme.txt"
    f.write_text("hello world\n")
    repo.index.add(["readme.txt"])

    diff = get_staged_diff(repo)
    assert "hello world" in diff


def test_commit_creates_commit(temp_repo):
    repo, path = temp_repo
    f = path / "new_file.txt"
    f.write_text("content\n")
    repo.index.add(["new_file.txt"])

    sha = commit(repo, "feat(demo): add new file")
    assert len(sha) == 7
    assert repo.head.commit.message.strip() == "feat(demo): add new file"


def test_changed_file_names(temp_repo):
    repo, path = temp_repo
    f = path / "another.txt"
    f.write_text("data\n")
    repo.index.add(["another.txt"])
    repo.index.commit("add another")

    # modify it and stage again
    f.write_text("data changed\n")
    repo.index.add(["another.txt"])

    names = get_changed_file_names(repo)
    assert "another.txt" in names
