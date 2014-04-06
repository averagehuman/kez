
import shutil
from tempfile import mkdtemp

import pytest
import peewee
from vcstools import get_vcs_client

from melba.models import Project, Document, Repository
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

def test_create_project(db):
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

def test_process_project_repository(vcs_cache):
    repo = Repository.instance("blog", vcs_cache)
    assert(len(list(Document.select()))) == 0
    repo.process()
    assert(len(list(Document.select()))) == 1

def test_delete_project(db):
    query = Project.select().where(Project.url==URL1)
    assert len(list(query)) == 1
    project = query[0]
    assert project.url == URL1
    dq = project.delete()
    assert isinstance(dq, peewee.DeleteQuery)
    dq.execute()
    query = Project.select().where(Project.url==URL1)
    assert len(list(query)) == 0


