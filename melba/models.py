
import os
import tempfile
import shutil

from peewee import Proxy, Model, SqliteDatabase
from peewee import CharField, ForeignKeyField, TextField, DateTimeField

from vcstools import get_vcs_client

from .exceptions import *
from .utils import ensure_dir, slugify, slugify_vcs_url, evaluate_config_options
from .utils import ConfigParser, NoOptionError
from .utils import ensure_dir, parse_vcs_url, syncfiles
from .builders import BuildController

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

class SluggedModel(BaseModel):
    slug = CharField(max_length=100)

    def set_slug(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        super(SluggedModel, self).__init__(*args, **kwargs)
        self.set_slug()

    def save(self, *args, **kwargs):
        self.set_slug()
        return super(SluggedModel, self).save(*args, **kwargs)

class Project(SluggedModel):
    name = CharField(max_length=20, unique=True)
    url = CharField(max_length=100, unique=True)
    vcs = CharField(max_length=20)
    host = CharField(max_length=30, null=True)
    owner = CharField(max_length=40, null=True)
    repo = CharField(max_length=40, null=True)
    version = CharField(max_length=40, null=True)

    @classmethod
    def from_url(cls, url, name=None):
        kwargs = parse_vcs_url(url)
        kwargs["name"] = name or kwargs.get("repo") or kwargs["slug"]
        return cls(**kwargs)
    
    def __str__(self):
        return self.name

    def set_slug(self):
        if hasattr(self, 'url') and self.url:
            self.slug = slugify_vcs_url(self.url)

    def get_repo_object(self, vcs_cache):
        return Repository(self, vcs_cache)

    def get_document(self, docname):
        return Document.select().join(Project).where(
            (Project.id == self.id) & (Document.name == docname)
        ).get()

    def get_document_set(self):
        return Document.select().join(Project).where(
            (Project.id == self.id)
        )

class Document(SluggedModel):
    project = ForeignKeyField(Project, related_name="documents")
    name = CharField(max_length=40, null=False)
    docroot = CharField(max_length=40, null=True)
    doctype = CharField(max_length=40)
    title = CharField(max_length=120, null=True)
    author = CharField(max_length=80, null=True)
    description = TextField(null=True)
    last_build = DateTimeField(null=True)

    def __str__(self):
        return self.name

    def set_slug(self):
        if (hasattr(self, 'name') and self.name) and (hasattr(self, 'project') and self.project):
            self.slug = slugify(self.project.name + ' ' + self.name)

    def set_docroot(self):
        if not hasattr(self, 'docroot') or self.docroot is None:
            self.docroot = ''
        self.docroot = self.docroot.strip('.').strip('/').strip('\\').strip('.')

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.set_docroot()

    def save(self, *args, **kwargs):
        self.set_docroot()
        return super(Document, self).save(*args, **kwargs)

class Repository(object):
    """A wrapper for a Project object that deals with that project's source repo"""

    @classmethod
    def instance(cls, project, vcs_cache):
        if isinstance(project, basestring):
            project = Project.get(Project.name == project)
        return cls(project, vcs_cache)

    def __init__(self, project, vcs_cache):
        self._project = project
        self._checkout = os.path.join(vcs_cache, project.slug)

    def _get_vcs_client(self):
        return get_vcs_client(self._project.vcs, self._checkout)

    def checkout(self):
        path = self._checkout
        # if checkout directory exists and is empty, remove it
        if pathexists(path) and os.path.isdir(path) and not os.listdir(path):
            os.rmdir(path)
        client = self._get_vcs_client()
        if not client.path_exists():
            client.checkout(self._project.url)
        client.update(version=self._project.version)

    def get_project_config(self):
        fpath = pathjoin(self._checkout, 'servus.cfg')
        if not pathexists(fpath):
            raise MissingOrInvalidConfig(fpath)
        cfg = ConfigParser()
        with open(fpath) as fp:
            cfg.readfp(fp)
        return cfg

    def process(self):
        """Read the project config file and create/update any documents defined there

        Return a list of `RepositoryDocument` objects.
        """
        existing = self._project.get_document_set()
        cfg = self.get_project_config()
        sections = cfg.sections()
        to_delete = set(obj.name for obj in existing) - set(sections)
        for section in sections:
            # each section relates to a single document
            kwargs = {}
            try:
                kwargs['docroot'] = cfg.get(section, 'docroot')
            except NoOptionError as e:
                kwargs['docroot'] = None
            kwargs['docroot'] = (kwargs['docroot'] or '').strip('.')
            try:
                kwargs['doctype'] = cfg.get(section, 'doctype')
            except NoOptionError as e:
                raise ConfigurationError(str(e))
            try:
                doc = self._project.get_document(section)
            except Document.DoesNotExist:
                kwargs['name'] = section
                kwargs['project'] = self._project
                doc = Document.create(**kwargs)
            else:
                for k,v in kwargs.items():
                    setattr(doc, k, v)
                doc.save()
        for docname in to_delete:
            doc = self._project.get_document(section)
            doc.delete_instance()
        docs = []
        for doc in self._project.get_document_set():
            options, settings = evaluate_config_options(cfg, doc.name)
            docs.append(
                RepositoryDocument(
                    self._project, doc, self._checkout, options, settings
                )
            )
        return docs

class RepositoryDocument(object):

    @classmethod
    def instance(cls, project, docname):
        return Document.select().join(Project).where(
            (Project.id == self.id) & (Document.name == docname)
        ).get()

    def __init__(self, project, document, vcs_path, options, settings):
        self.project = project
        self.document = document
        self.vcs_path = vcs_path.rstrip('/')
        self.options = options
        self.settings = settings
        self.dst = None

    @property
    def name(self):
        return self.document.name

    @property
    def slug(self):
        return self.document.slug

    def __str__(self):
        return "[%s] %s " % (self.project, self.document)

    def build(self, dst=None, dstroot=None, option_overrides=None):
        if not any([dst, dstroot]):
            raise Exception("a destination directory or a destination root directory must be given")
        src = pathjoin(self.vcs_path, self.document.docroot)
        tmp = tempfile.mkdtemp(prefix='melba-', suffix='-'+self.document.doctype)
        self.dst = dst or pathjoin(dstroot, self.document.slug)
        options = self.options.copy()
        if option_overrides:
            options.update(option_overrides)
        controller = BuildController(
            self.document.doctype, src, tmp, options, self.settings
        )
        controller.build()
        syncfiles(tmp, self.dst)
        try:
            shutil.rmtree(tmp)
        except:
            pass

