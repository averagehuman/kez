
import pytest

from melba.exceptions import *

from .data import *

def test_add_repo(manager):
    assert len(manager.list_repos()) == 0
    repo = manager.add_repo(url=URL1)
    assert repo
    assert repo.url == URL1
    assert len(manager.list_repos()) == 1

def test_duplicate_repo_error(manager):
    with pytest.raises(RepoExistsError) as exc_info:
        manager.add_repo(url=URL1)

def test_delete_repo(manager):
    assert len(manager.list_repos()) == 1
    ret = manager.delete_repo(URL1)
    assert ret == 1
    assert len(manager.list_repos()) == 0

