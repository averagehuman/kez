
from peewee import Proxy, Model
from peewee import CharField, ForeignKeyField, TextField, DateTimeField

_db = Proxy()

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

