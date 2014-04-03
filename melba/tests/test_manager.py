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

def test_add_project(manager):
    assert len(manager.list_projects()) == 0
    project = manager.add_project("blog", URL1)
    assert project
    assert project.url == URL1
    assert len(manager.list_projects()) == 1

def test_duplicate_project_error(manager):
    with pytest.raises(ObjectExistsError) as exc_info:
        manager.add_project("blog", URL1)

def test_delete_project(manager):
    assert len(manager.list_projects()) == 1
    ret = manager.delete_project("blog")
    assert ret == 1
    assert len(manager.list_projects()) == 0
