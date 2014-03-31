
import os
import sys
import argparse

from cliff.command import Command

from melba.manager import LocalManager as Local


def args_to_dict(arglist):
    kw = {}
    for arg in arglist:
        k, equals, v = arg.partition('=')
        if not (k and equals and v):
            raise ValueError("invalid parameter %s" % arg)
        kw[k.strip('-').strip()] = v.strip()
    return kw
