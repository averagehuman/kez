
kez
===

A simple command line utility for tracking and building documents, specifically
*Pelican* blogs. Uses *cliff* and a local sqlite database object-mapped with
*peewee*. Tested with Python2 and Python3.

Supported Document Types
------------------------

+ Pelican

In the future, possibly *Sphinx*.


Required
--------

The following libraries are required:

+ cliff
+ pelican
+ peewee
+ vcstools
+ giturlparse.py
+ watdarepo
+ python-slugify
+ TypedInterpolation


Tests
-----

Run tests with *Python 2* or *Python 3*:

    $ make test
    $ make test PYVERSION=2
    $ make test PYVERSION=3

*Python 3* is the default if PYVERSION is not specified.


