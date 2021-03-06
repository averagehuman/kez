# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import os
import tempfile
import shutil

import pytest

from kez.builders.pelican.builder import build as build_pelican

from .data import *

pathexists = os.path.exists
pathjoin = os.path.join

def example_settings():
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
    return settings

def test_pelican_raw_build(storage_root, vcs_cache):
    src = pathjoin(storage_root, 'pelican', 'samples', 'advanced')
    dst = tempfile.mkdtemp(prefix="kez-")
    assert pathexists(src)
    assert not os.listdir(dst)
    settings = example_settings()
    build_pelican(src, dst, vcs_cache, {}, settings)
    assert "index.html" in os.listdir(dst)
    shutil.rmtree(dst)

def test_pelican_repository_build(manager):
    project = None
    for proj in manager.list_projects():
        if proj.url == URL1:
            project = proj
            break
    else:
        project = manager.add_project("blog", URL1)
    count = len(manager.list_projects())
    docs = manager.build_project(project.name)
    assert len(docs) == 1
    document = docs[0].document
    assert document.local_root
    html_index = document.get_html_index()
    assert html_index
    assert os.path.exists(html_index)
    manager.delete_project("blog")
    assert len(manager.list_projects()) == count - 1

def test_pelican_with_remote_theme(storage_root, vcs_cache):
    src = pathjoin(storage_root, 'pelican', 'samples', 'advanced')
    dst = tempfile.mkdtemp(prefix="kez-")
    assert pathexists(src)
    assert not os.listdir(dst)
    settings = example_settings()
    settings["THEME"] = ""
    settings["THEME_URL"] = "git@github.com:fjavieralba/flasky.git"
    build_pelican(src, dst, vcs_cache, {}, settings)
    assert "index.html" in os.listdir(dst)
    shutil.rmtree(dst)

