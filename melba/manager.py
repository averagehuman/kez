
import os
import sys

pathjoin = os.path.join
pathexists = os.path.exists
pathsplit = os.path.splitext

class LocalManager(object):

    def __init__(self, rootdir):
        self.rootdir = rootdir

