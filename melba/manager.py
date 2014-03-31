
import os
import sys

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

from .models import _db, Repo, Document

class Manager(object):

    def __init__(self, database):
        if _db.obj is None:
            _db.initialize(database)
            Repo.create_table(fail_silently=True)
            Document.create_table(fail_silently=True)
        self.db = _db

    def add_repo(self, url):
        Repo.create(url=url)

