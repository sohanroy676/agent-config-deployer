"""Tests for core/git_handler.py."""

import pytest

from core.git_handler import GitCloneError, _repo_name_from_url, clone_repo


def test_repo_name_from_https_url():
    assert _repo_name_from_url("https://github.com/user/my-repo.git") == "my-repo"
    assert _repo_name_from_url("https://github.com/user/my-repo") == "my-repo"


def test_repo_name_from_ssh_url():
    assert _repo_name_from_url("git@github.com:user/my-repo.git") == "my-repo"


def test_repo_name_from_url_with_trailing_slash():
    assert _repo_name_from_url("https://github.com/user/my-repo/") == "my-repo"


def test_repo_name_empty_for_bare_url():
    assert _repo_name_from_url("https://github.com/") == ""


def test_clone_repo_missing_parent_dir(tmp_path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(GitCloneError):
        clone_repo("https://github.com/user/repo.git", missing)


def test_clone_repo_target_exists(tmp_path):
    parent = tmp_path / "parent"
    parent.mkdir()
    (parent / "repo").mkdir()
    with pytest.raises(GitCloneError):
        clone_repo("https://github.com/user/repo.git", parent)


def test_clone_repo_invalid_url(tmp_path):
    parent = tmp_path / "parent"
    parent.mkdir()
    with pytest.raises(GitCloneError):
        clone_repo("not-a-valid-url", parent)


def test_clone_repo_success(tmp_path):
    """Clone a real public repo into a temp parent and verify the folder exists."""
    parent = tmp_path / "parent"
    parent.mkdir()
    result = clone_repo("https://github.com/octocat/Hello-World.git", parent)
    assert result.exists()
    assert result.is_dir()
    assert (result / ".git").exists()
