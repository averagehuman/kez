
import os
import sys

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

from peewee import IntegrityError
from watdarepo import watdarepo
from giturlparse import parse as giturlparse

from .models import Project, Document, Repository
from .utils import ensure_dir
from .exceptions import *

class Manager(object):

    def __init__(self, database, storage_root):
        self.db = database
        self.vcs_cache = os.path.join(storage_root, '__VCS__')
        ensure_dir(self.vcs_cache)

    def _get_project_repo(self, project):
        return Repository(project, self.vcs_cache)

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
        # create a new Project instance
        project = Project(**kwargs)
        # checkout project repo and ensure a valid config file before saving
        repo = project.get_repo_object(self.vcs_cache)
        repo.checkout()
        repo.get_project_config()
        # save and return project
        project.save()
        return project

    def list_projects(self):
        return list(Project.select())

    def delete_project(self, name):
        q = Project.delete().where(Project.name==name)
        return q.execute()

    def add_s3_credentials(self, name=None):
        pass

    def _update_project(self, project, noclobber=False):
        repo = project.get_repo_object(self.vcs_cache)
        orphans, docs = repo.get_or_create_documents()
        if not noclobber:
            for doc in orphans:
                doc.delete()

    def update_project(self, name):
        pass

    def build_project(self, name):
        repo = Repository.instance(name, self.vcs_cache)
        return docs

    def build_all(self):
        pass


