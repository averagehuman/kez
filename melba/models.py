
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
    Repo.create_table(fail_silently=True)
    Document.create_table(fail_silently=True)

class BaseModel(Model):
    class Meta:
        database = _db

class Repo(BaseModel):
    url = CharField(max_length=100, unique=True)

class Document(BaseModel):
    repo = ForeignKeyField(Repo, related_name="documents")
    title = CharField(max_length=120, null=False)
    author = CharField(max_length=80, null=True)
    description = TextField(null=True)
    last_build = DateTimeField(null=True)

