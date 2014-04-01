
import os
import pytest
from melba.models import sqlite_proxy

_data_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

_proxy = None

@pytest.fixture
def db():
    global _proxy
    if _proxy is None:
        db_path = os.path.join(_data_root, 'example.db')
        if os.path.exists(db_path):
            os.remove(db_path)
        _proxy = sqlite_proxy(db_path)
    return _proxy

@pytest.fixture
def File():
    def FileOpener(relpath, mode="rb"):
        return FileProxy(open(os.path.join(_data_root, relpath.lstrip('/')), mode))
    return FileOpener

