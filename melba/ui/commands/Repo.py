
import argparse

from .base import BaseCommand, args_to_dict

class Add(BaseCommand):
    """Add a new source code repository
    
    Eg. melba add repo git://git@github.com/averagehuman/maths.averagehuman.org
    """
    

    def get_parser(self, prog_name):
        parser = super(Repo, self).get_parser(prog_name)
        parser.add_argument(
            'url',
            help="the url of a code repository containing document sources",
        )
        return parser

    def take_action(self, args):
        self.manager.add_repo(args.url)

