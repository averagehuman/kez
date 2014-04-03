
import pytest

import peewee

from melba.models import Project, Document

from .data import *


def test_create_repo(db):
    query = list(Project.select())
    assert len(query) == 0
    project = Project.create(name="blog", url=URL1)
    assert project
    assert project.url == URL1
    query = list(Project.select())
    assert len(query) == 1
    assert query[0].url == URL1

def test_empty_and_non_empty_query():
    query = Project.select().where(Project.url=="doesnotexist")
    assert len(list(query)) == 0
    query = Project.select().where(Project.url==URL1)
    assert len(list(query)) == 1

def test_delete_repo(db):
    query = Project.select().where(Project.url==URL1)
    assert len(list(query)) == 1
    project = query[0]
    assert project.url == URL1
    dq = project.delete()
    assert isinstance(dq, peewee.DeleteQuery)
    dq.execute()
    query = Project.select().where(Project.url==URL1)
    assert len(list(query)) == 0

