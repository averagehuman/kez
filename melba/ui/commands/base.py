
import os
import sys
import argparse

from cliff.command import Command
from peewee import SqliteDatabase

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
            db_root_dir = os.path.dirname(db_path)
            if not os.path.exists(db_root_dir):
                os.makedirs(db_root_dir)
            self._manager = Manager(SqliteDatabase(db_path))
        return self._manager

