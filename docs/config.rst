
Configuration
=============

The `kez` config file must be called `kez.cfg` and placed at the root level
of the repository.  It is an ini-style file with one or many sections, where
each section defines a particular document. The `__docroot__` value in each
section should give the directory, relative to the config file, where the
document sources are located (defaulting to the config file's directory).

By convention, a lowercase key relates to a build meta-option, while an
uppercase key is an option required or with meaning to the program which
is called to produce the document (eg. Sphinx, Pelican,..).


Example
-------

::

    [maths.averagehuman.org]
    __docroot__ = blog
    __doctype__ = pelican
    AUTHOR = Professor Strange
    SITENAME = Average Maths
    SITEURL = maths.averagehuman.org
    ARTICLE_URL = {date:%Y}/{date:%m}/{slug}/
    ARTICLE_LANG_URL = {date:%Y}/{date:%m}/{lang}/{slug}/
    PAGE_URL = {slug}/
    PAGE_LANG_URL = {lang}/{slug}/
    ARTICLE_SAVE_AS = {date:%Y}/{date:%m}/{slug}/index.html
    ARTICLE_LANG_SAVE_AS = {lang}/{date:%Y}/{date:%m}/{slug}/index.html
    PAGE_SAVE_AS = {slug}/index.html
    PAGE_LANG_SAVE_AS = {lang}/{slug}/index.html

