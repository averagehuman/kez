
import os
from ConfigParser import ConfigParser, NoOptionError

from peewee import Proxy, Model, SqliteDatabase
from peewee import CharField, ForeignKeyField, TextField, DateTimeField

from vcstools import get_vcs_client

from .exceptions import *
from .utils import ensure_dir, slugify_vcs_url

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

_db = Proxy()

def sqlite_proxy(db_path):
    if _db.obj is not None:
        raise Exception("proxy is already initialised")
    db_root_dir = os.path.dirname(db_path)
    if not os.path.exists(db_root_dir):
        os.makedirs(db_root_dir)
    _db.initialize(SqliteDatabase(db_path))
    _create_tables()
    return _db

def _create_tables():
    Project.create_table(fail_silently=True)
    Document.create_table(fail_silently=True)

class BaseModel(Model):
    class Meta:
        database = _db

class Project(BaseModel):
    name = CharField(max_length=20, unique=True)
    url = CharField(max_length=100, unique=True)
    slug = CharField(max_length=100)
    vcs = CharField(max_length=20, null=True)
    host = CharField(max_length=30, null=True)
    owner = CharField(max_length=40, null=True)
    repo = CharField(max_length=40, null=True)
    version = CharField(max_length=40, null=True)

    def _set_slug(self):
        if (hasattr(self, 'url') and self.url) and (not hasattr(self, 'slug') or not self.slug):
            self.slug = slugify_vcs_url(self.url)

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self._set_slug()

    def save(self, *args, **kwargs):
        self._set_slug()
        return super(Project, self).save(*args, **kwargs)

    def get_repo_object(self, vcs_cache):
        return Repository(self, vcs_cache)

    def get_document(self, docname):
        return Document.select().join(Project).where(
            (Project.name == self.name) & (Document.name == docname)
        ).get()

class Document(BaseModel):
    project = ForeignKeyField(Project, related_name="documents")
    name = CharField(max_length=40, null=False)
    docroot = CharField(max_length=40)
    doctype = CharField(max_length=40)
    title = CharField(max_length=120, null=True)
    author = CharField(max_length=80, null=True)
    description = TextField(null=True)
    last_build = DateTimeField(null=True)

class Repository(object):
    """A wrapper for a Project object that deals with that project's source repo"""

    @classmethod
    def instance(cls, project_name, vcs_cache):
        project = Project.get(Project.name == project_name)
        return cls(project, vcs_cache)

    def __init__(self, project, vcs_cache):
        self._project = project
        self._checkout = os.path.join(vcs_cache, project.slug)

    def __getattr__(self, key):
        return getattr(self._project, key)

    def _get_vcs_client(self):
        return get_vcs_client(self.vcs, self._checkout)

    def checkout(self):
        path = self._checkout
        # if checkout directory exists and is empty, remove it
        if pathexists(path) and os.path.isdir(path) and not os.listdir(path):
            os.rmdir(path)
        client = self._get_vcs_client()
        if not client.path_exists():
            client.checkout(self.url)
        if self.version:
            client.update(version=self.version)

    def get_project_config(self):
        fpath = pathjoin(self._checkout, 'servus.cfg')
        if not pathexists(fpath):
            raise MissingOrInvalidConfig(fpath)
        cfg = ConfigParser()
        with open(fpath) as fp:
            cfg.readfp(fp)
        return cfg

    def process(self):
        existing = Document.select().join(Project).where(
            Project.name == self.name
        )
        cfg = self.get_project_config()
        sections = cfg.sections()
        to_delete = set(obj.name for name in existing) - set(sections)
        for section in sections:
            # each section relates to a single document
            kwargs = {}
            try:
                kwargs['docroot'] = cfg.get(section,'docroot')
            except NoOptionError, e:
                kwargs['docroot'] = '.'
            try:
                kwargs['doctype'] = cfg.get(section,'doctype')
            except NoOptionError, e:
                raise ConfigurationError(str(e))
            kwargs['name'] = section
            kwargs['project'] = self._project
            try:
                doc = self._project.get_document(section)
            except Document.DoesNotExist:
                doc = Document.create(**kwargs)
            else:
                for k,v in kwargs.items():
                    setattr(doc, k, v)
                doc.save()
        for docname in to_delete:
            doc = self._project.get_document(section)
            doc.delete_instance()


