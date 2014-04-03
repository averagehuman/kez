
import argparse

from cliff.lister import Lister
from melba.exceptions import *
from melba.models import Repo, Document
from .base import BaseCommand, BaseLister, args_to_dict

class Add(BaseCommand):
    """Add a new source code repository
    
    Eg. melba add repo git://git@github.com/averagehuman/maths.averagehuman.org
    """

    def get_parser(self, prog_name):
        parser = super(Add, self).get_parser(prog_name)
        parser.add_argument(
            'url',
            help="the url of a code repository containing document sources",
        )
        return parser

    def take_action(self, args):
        try:
            repo = self.manager.add_repo(args.url)
        except RepoExistsError:
            self.app.stderr.write("That repository already exists.\n")
        except Exception, e:
            self.app.stderr.write("ERROR: %s\n" % e)

class List(BaseLister):
    """List all repos"""

    def take_action(self, args):
        def iterobjects():
            for repo in self.manager.list_repos():
                yield repo.host, repo.vcs, repo.owner, repo.name, repo.url
        return (
            ('Host', 'Type', 'Owner', 'Name', 'Url'),
            sorted(iterobjects()),
        )

