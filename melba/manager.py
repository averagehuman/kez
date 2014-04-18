
import os
import sys

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

from peewee import IntegrityError

from .models import Project, Document, Repository
from .utils import ensure_dir, parse_vcs_url
from .exceptions import *

class Manager(object):

    def __init__(self, database, storage_root):
        self.db = database
        self.vcs_cache = os.path.join(storage_root, '__VCS__')
        self.build_cache = os.path.join(storage_root, '__BUILD__')
        ensure_dir(self.vcs_cache)

    def _get_project_repo(self, project):
        return Repository(project, self.vcs_cache)

    def add_project(self, name, url):
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
        project = Project.from_url(url, name=name)
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

    def update_project(self, name):
        pass

    def build_project(self, project, docnames=None, output_path=None, stdout=sys.stdout):
        """
        Build all project documents OR, if docnames are given, one or more specific documents.
        """
        docnames = docnames or []
        output_path = output_path or self.build_cache
        repo = Repository.instance(project, self.vcs_cache)
        if not docnames:
            docs = repo.process()
        else:
            docs = []
            for doc in repo.process():
                if doc.name in docnames:
                    docs.append(doc)
            invalid = set(docnames) - set(doc.name for doc in docs)
            if invalid:
                raise UnknownDocumentError(project, list(invalid)[0])
        for d in docs:
            stdout.write("***** STARTED BUILDING: %s *****\n" % d)
            d.build(dstroot=output_path)
            stdout.write("***** FINISHED: %s *****\n" % d)
        return docs

    def serve_document(self, projectname, docname=None):
        project = Project.get(Project.name == projectname)
        doc = project.get_document(docname)
        page = doc.get_html_index()
        if not page:
            raise NoDocumentIndexError
        import webbrowser as wb
        wb.open(r'file:///' + page)
