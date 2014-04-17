
import os
import sys
import argparse

from cliff.command import Command
from cliff.lister import Lister

from melba.exceptions import *
from melba.manager import Manager
from melba.models import sqlite_proxy, Project, Document

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

class List(BaseLister):
    """List all projects"""

    def take_action(self, args):
        def iterobjects():
            for project in self.manager.list_projects():
                yield project.name, project.host, project.owner, project.repo, project.url
        return (
            ('Name', 'Host', 'Owner', 'Repo', 'Url'),
            sorted(iterobjects()),
        )

class Add(BaseCommand):
    """Add a new project
    
    Eg. melba add blog git://git@<repo>
    """

    def get_parser(self, prog_name):
        parser = super(Add, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help="the name of the new project",
        )
        parser.add_argument(
            'url',
            help="the url of a code repository containing document sources",
        )
        return parser

    def take_action(self, args):
        try:
            project = self.manager.add_project(args.name, args.url)
        except URLFormatError:
            self.app.stderr.write("Invalid url.\n")
        except ObjectExistsError:
            self.app.stderr.write("That project already exists.\n")
        except Exception as e:
            self.app.stderr.write("ERROR: %s\n" % e)

class Build(BaseCommand):
    """Build project documents
    
    Eg.

    Build all project documents:

        $ melba build phd

    Build one or more specific documents in a project:

        $ melba build phd prelim-findings bibliography

    """

    def get_parser(self, prog_name):
        parser = super(Build, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            help="the name of a registered project",
        )
        parser.add_argument(
            'docs',
            nargs='*',
            help="optionally specify one or many documents to build",
        )
        parser.add_argument(
            '-o',
            '--output-path',
            action='store',
            dest='output_path',
            help="the path to a directory to place the project's built documents",
        )
        return parser

    def take_action(self, args):
        try:
            self.manager.build_project(
                args.project, docnames=args.docs, output_path=args.output_path,
                stdout=self.app.stdout,
            )
        except Exception as e:
            self.app.stderr.write("ERROR: %s\n" % e)

