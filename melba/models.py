
import os

from peewee import Proxy, Model, SqliteDatabase
from peewee import CharField, ForeignKeyField, TextField, DateTimeField

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
    vcs = CharField(max_length=20, null=True)
    host = CharField(max_length=30, null=True)
    owner = CharField(max_length=40, null=True)
    repo = CharField(max_length=40, null=True)
    slug = CharField(max_length=100, null=True)
    version = CharField(max_length=40, null=True)

class Document(BaseModel):
    project = ForeignKeyField(Project, related_name="documents")
    title = CharField(max_length=120, null=False)
    author = CharField(max_length=80, null=True)
    description = TextField(null=True)
    last_build = DateTimeField(null=True)

