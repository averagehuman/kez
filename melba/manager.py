
import os
import sys

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

from peewee import IntegrityError

from .models import Repo, Document

class Manager(object):

    def __init__(self, database):
        self.db = database

    def add_repo(self, url):
        repo = Repo.create(url=url)
        return repo

    def list_repos(self):
        return list(Repo.select())

    def delete_repo(self, url):
        q = Repo.delete().where(Repo.url==url)
        return q.execute()

