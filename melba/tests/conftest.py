
import os
import pytest

from melba.models import sqlite_proxy
from melba.manager import Manager

from .data import STORAGE_ROOT

_proxy = None

@pytest.fixture
def storage_root():
    return STORAGE_ROOT

@pytest.fixture
def db():
    global _proxy
    if _proxy is None:
        db_path = os.path.join(STORAGE_ROOT, 'example.db')
        if os.path.exists(db_path):
            os.remove(db_path)
        _proxy = sqlite_proxy(db_path)
    return _proxy

@pytest.fixture
def manager(db, storage_root):
    return Manager(db, storage_root)

@pytest.fixture
def File():
    def FileOpener(relpath, mode="rb"):
        return FileProxy(open(os.path.join(STORAGE_ROOT, relpath.lstrip('/')), mode))
    return FileOpener
