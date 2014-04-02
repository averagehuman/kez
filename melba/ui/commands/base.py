
import os
import sys
import argparse

from cliff.command import Command

from melba.models import sqlite_proxy
from melba.manager import Manager


def args_to_dict(arglist):
    kw = {}
    for arg in arglist:
        k, equals, v = arg.partition('=')
        if not (k and equals and v):
            raise ValueError("invalid parameter %s" % arg)
        kw[k.strip('-').strip()] = v.strip()
    return kw

class BaseCommand(Command):

    def __init__(self, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self._manager = None

    @property
    def manager(self):
        if self._manager is None:
            db_path = self.app.options.data_path
            storage_root = os.path.dirname(db_path)
            self._manager = Manager(sqlite_proxy(db_path), storage_root)
        return self._manager

