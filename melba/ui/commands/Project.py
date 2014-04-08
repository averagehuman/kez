
import argparse

from cliff.lister import Lister
from melba.exceptions import *
from melba.models import Project, Document
from .base import BaseCommand, BaseLister, args_to_dict

class List(BaseLister):
    """List all registered projects"""

    def take_action(self, args):
        def iterobjects():
            for project in self.manager.list_projects():
                yield project.name, project.host, project.owner, project.name, project.url
        return (
            ('Name', 'Host', 'Owner', 'Repo', 'Url'),
            sorted(iterobjects()),
        )

class Add(BaseCommand):
    """Add a new source code repository
    
    Eg. melba project add "maths-blog" git://git@github.com/averagehuman/maths.averagehuman.org
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
        except Exception, e:
            self.app.stderr.write("ERROR: %s\n" % e)

class Build(BaseCommand):
    """Build all documents for a given project
    
    Eg. melba project build "maths-blog"
    """

    def get_parser(self, prog_name):
        parser = super(Add, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            help="the name of a registered project",
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
            docs = self.manager.build_project(args.name, output_path=args.output_path)
            for doc in docs:
                self.app.stdout.write("%s\n" % doc.name)
        except Exception, e:
            self.app.stderr.write("ERROR: %s\n" % e)

