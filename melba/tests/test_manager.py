import shutil
from tempfile import mkdtemp

import pytest

from vcstools import get_vcs_client

from melba.exceptions import *

from .data import *

pathexists = os.path.exists
pathjoin = os.path.join

def test_vcs_checkout():
    tmp= mkdtemp(prefix="melba-test")
    git = pathjoin(tmp, '.git')
    assert not pathexists(git)
    client = get_vcs_client("git", tmp)
    client.checkout(URL1)
    assert pathexists(git)
    shutil.rmtree(tmp)

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

