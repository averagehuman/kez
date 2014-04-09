# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import os
import tempfile
import shutil

import pytest

from melba.builders.pelican.builder import build as build_pelican

from .data import *

pathexists = os.path.exists
pathjoin = os.path.join

def test_pelican_raw_build(storage_root):
    src = pathjoin(storage_root, 'pelican', 'samples', 'advanced')
    dst = tempfile.mkdtemp(prefix="melba-")
    assert pathexists(src)
    settings = {}
    settings["AUTHOR"] = 'Alexis Métaireau'
    settings["SITENAME"] = "Alexis' log"
    settings["SITEURL"] = 'http://blog.notmyidea.org'
    settings["TIMEZONE"] = "Europe/Paris"
    settings["RELATIVE_URLS"] = True
    settings["PATH"] = 'content'
    settings["STATIC_PATHS"] = [
        'pictures',
        'cat1',
        'extra/robots.txt',
    ]
    settings["PYGMENTS_RST_OPTIONS"] = {'linenos': 'table'}
    settings["REVERSE_CATEGORY_ORDER"] = True
    settings["LOCALE"] = "C"
    settings["DEFAULT_PAGINATION"] = 4
    settings["DEFAULT_DATE"] = (2012, 3, 2, 14, 1, 1)
    assert not os.listdir(dst)
    build_pelican(src, dst, {}, settings)
    assert os.listdir(dst)
    shutil.rmtree(dst)

def test_pelican_repository_build(manager):
    project = None
    for proj in manager.list_projects():
        if proj.url == URL1:
            project = proj
            break
    else:
        project = manager.add_project("blog", URL1)
    docs = manager.build_project(project.name)
    assert len(docs) == 1

