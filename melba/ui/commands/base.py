
import os
import sys
import argparse
import abc

from cliff.command import Command
from cliff.lister import Lister

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

class ManagerMixin(object):

    @property
    def manager(self):
        try:
            return self._manager
        except AttributeError:
            db_path = self.app.options.data_path
            storage_root = os.path.dirname(db_path)
            self._manager = Manager(sqlite_proxy(db_path), storage_root)
        return self._manager

class BaseCommand(Command, ManagerMixin):
    pass

class BaseLister(Lister, ManagerMixin):
    pass

