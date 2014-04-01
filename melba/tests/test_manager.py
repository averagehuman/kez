
import pytest

from melba.models import Repo, Document
from melba.manager import Manager

from .data import *

def test_add_and_delete_repo(db):
    manager = Manager(db)
    repo = manager.add_repo(url=URL1)
    assert repo
    assert repo.url == URL1
    repos = manager.list_repos()
    assert len(repos) == 1
    ret = manager.delete_repo(URL1)
    assert ret == 1
    repos = manager.list_repos()
    assert len(repos) == 0


