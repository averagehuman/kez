
import os
import tempfile
import shutil

import pytest

from melba.builders.pelican.builder import build as build_pelican

pathexists = os.path.exists
pathjoin = os.path.join

def test_pelican_build(storage_root):
    src = pathjoin(storage_root, 'pelican', 'samples', 'advanced')
    dst = tempfile.mkdtemp(prefix="melba-")
    assert pathexists(src)
    build_pelican(src, dst, {}, {})
    assert dst == None

