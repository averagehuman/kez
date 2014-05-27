
kez
===

A simple command line utility for tracking and building documents, specifically
[Pelican](http://docs.getpelican.com) blogs.

Uses [cliff](http://cliff.readthedocs.org) for the user interface, together
with a local sqlite database object-mapped with
[peewee](http://peewee.readthedocs.org).

Tested with Python-2.7 and Python-3.4. Unlikely to work on windows.

Usage
-----

Add a repository containing document source files:

    $ kez add myblog git@github.com:averagehuman/maths.averagehuman.org.git

If there is a valid **kez.cfg** present in the repository root, build any
documents defined therein:

    $ kez build myblog

Track projects:

    $ kez list
    +---------+------------------------+---------+--------------------------------------------------------+
    | Project | Document               | Type    | Url                                                    |
    +---------+------------------------+---------+--------------------------------------------------------+
    | myblog  | maths.averagehuman.org | PELICAN | git@github.com:averagehuman/maths.averagehuman.org.git |
    +---------+------------------------+---------+--------------------------------------------------------+

After building, if there is a root *index.html*, open the document in a browser window:

    $ kez serve myblog

TODO
''''

Support uploading the built files to a remote server.

Configuration
-------------

The source repository must have an ini-style config file called **kez.cfg**
containing one or many sections, where each section defines a particular
document.  The **\_\_docroot\_\_** value in each section
should give the directory, relative to the config file, where the document
sources are located (defaulting to the config file's directory).

By convention, a double-underscored key is a build meta-option, while any
other key is an option required or with meaning to the program which
is called to produce the document (eg. Sphinx, Pelican,..).


Example **kez.cfg**
-------------------

    [maths.averagehuman.org]
    __doctype__ = pelican
    AUTHOR = Buzz Lightyear (MSc Phd)
    SITENAME = Beyond Infinity
    SITEURL = blog.beyondinfinity.net
    ARTICLE_URL = {date:%%Y}/{date:%%m}/{slug}/
    ARTICLE_LANG_URL = {date:%%Y}/{date:%%m}/{lang}/{slug}/
    PAGE_URL = {slug}/
    PAGE_LANG_URL = {lang}/{slug}/
    ARTICLE_SAVE_AS = {date:%%Y}/{date:%%m}/{slug}/index.html
    ARTICLE_LANG_SAVE_AS = {lang}/{date:%%Y}/{date:%%m}/{slug}/index.html
    PAGE_SAVE_AS = {slug}/index.html
    PAGE_LANG_SAVE_AS = {lang}/{slug}/index.html


Supported Document Types
------------------------

+ Pelican

In the future, possibly *Sphinx*.

Pelican Themes
--------------

Pelican theme files can be included in the document repository and enabled by
setting the **THEME** config option to the relative path to those files.

    THEME = path/to/theme

Alternatively, there is a **THEME_URL** setting which can be set to a
git/mercurial repo.  If the theme files are in some subdirectory of the repo,
then set **THEME** to the appropriate relative path, otherwise **THEME** should
not be present or be null.

So, either:

    THEME_URL = git@github.com:awsomhakr/awsomhakr-theme.git

or:

    THEME_URL = git@github.com:getpelican/pelican-themes.git
    THEME = bootstrap2

Required
--------

The following libraries are required:

+ [cliff](http://cliff.readthedocs.org)
+ [pelican](http://docs.getpelican.com)
+ [peewee](http://peewee.readthedocs.org)
+ [vcstools](https://pypi.python.org/pypi/vcstools/)
+ [giturlparse.py](https://pypi.python.org/pypi/giturlparse.py/)
+ [watdarepo](https://pypi.python.org/pypi/watdarepo/)
+ [python-slugify](https://pypi.python.org/pypi/python-slugify/)
+ [TypedInterpolation](https://pypi.python.org/pypi/TypedInterpolation/)


Tests
-----

Run tests with *Python 2* or *Python 3*:

    $ make test
    $ make test PYVERSION=2
    $ make test PYVERSION=3

*Python 3* is the default if PYVERSION is not specified.


