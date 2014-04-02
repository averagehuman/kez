
import os
import sys

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

from peewee import IntegrityError
from watdarepo import watdarepo
from giturlparse import parse as giturlparse
import mayo

from .models import Repo, Document
from .utils import ensure_dir
from .exceptions import *

class Manager(object):

    def __init__(self, database, storage_root):
        self.db = database
        self.vcs_cache = os.path.join(storage_root, '__VCS__')
        ensure_dir(self.vcs_cache)

    def add_repo(self, url):
        wat = watdarepo(url)
        kwargs = {
            "vcs": wat["vcs"],
            "host": wat["hosting_service"],
            "url": url,
        }
        if wat["vcs"] == "git":
            parsed = giturlparse(url)
            if not parsed.valid:
                raise URLFormatError(url)
            kwargs["host"] = parsed.host
            kwargs["owner"] = parsed.owner
            kwargs["slug"] = parsed.repo
            kwargs["url"] = parsed.url2ssh
        try:
            Repo.get(Repo.url == url)
        except Repo.DoesNotExist:
            pass
        else:
            raise RepoExistsError(url)
        self._process_repo(**kwargs)
        repo = Repo.create(**kwargs)
        return repo

    def list_repos(self):
        return list(Repo.select())

    def delete_repo(self, url):
        q = Repo.delete().where(Repo.url==url)
        return q.execute()

    def _process_repo(self, **kwargs):
        pass

