
kez
===

A simple command line utility for tracking and building documents, specifically
[Pelican](http://docs.getpelican.com) blogs.

Uses [cliff](http://cliff.readthedocs.org) and a local sqlite database
object-mapped with [peewee](http://peewee.readthedocs.org).

Tested with Python-2.7 and Python-3.4

Supported Document Types
------------------------

+ Pelican

In the future, possibly *Sphinx*.


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


