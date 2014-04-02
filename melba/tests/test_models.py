
import pytest

import peewee

from melba.models import Repo, Document

from .data import *


def test_create_repo(db):
    query = list(Repo.select())
    assert len(query) == 0
    repo = Repo.create(url=URL1)
    assert repo
    assert repo.url == URL1
    query = list(Repo.select())
    assert len(query) == 1
    assert query[0].url == URL1

def test_empty_and_non_empty_query():
    query = Repo.select().where(Repo.url=="doesnotexist")
    assert len(list(query)) == 0
    query = Repo.select().where(Repo.url==URL1)
    assert len(list(query)) == 1

def test_delete_repo(db):
    query = Repo.select().where(Repo.url==URL1)
    assert len(list(query)) == 1
    repo = query[0]
    assert repo.url == URL1
    dq = repo.delete()
    assert isinstance(dq, peewee.DeleteQuery)
    dq.execute()
    query = Repo.select().where(Repo.url==URL1)
    assert len(list(query)) == 0

