
import os
import sys

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

from peewee import IntegrityError
from watdarepo import watdarepo
from giturlparse import parse as giturlparse
from vcstools import get_vcs_client

from .models import Project, Document
from .utils import ensure_dir, slugify_vcs_url
from .exceptions import *

class Manager(object):

    def __init__(self, database, storage_root):
        self.db = database
        self.vcs_cache = os.path.join(storage_root, '__VCS__')
        ensure_dir(self.vcs_cache)

    def _checkout_or_update_repo(self, **kwargs):
        checkout = os.path.join(
            self.vcs_cache, kwargs["slug"]
        )
        # if checkout directory exists and is empty, remove it
        if pathexists(checkout) and os.path.isdir(checkout) and not os.listdir(checkout):
            os.rmdir(checkout)
        client = get_vcs_client(kwargs["vcs"], checkout)
        if not client.path_exists():
            client.checkout(kwargs["url"])
        if kwargs.get("version"):
            client.update(version=kwargs["version"])

    def add_project(self, name, url):
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
            kwargs["repo"] = parsed.repo
            kwargs["url"] = parsed.url2ssh
        kwargs["name"] = name
        kwargs["slug"] = slugify_vcs_url(kwargs["url"])
        kwargs["version"] = None
        try:
            Project.get(Project.url == url)
        except Project.DoesNotExist:
            pass
        else:
            raise ObjectExistsError(url)
        try:
            Project.get(Project.name == name)
        except Project.DoesNotExist:
            pass
        else:
            raise ObjectExistsError(name)
        self._checkout_or_update_repo(**kwargs)
        project = Project.create(**kwargs)
        return project

    def list_projects(self):
        return list(Project.select())

    def delete_project(self, name):
        q = Project.delete().where(Project.name==name)
        return q.execute()

