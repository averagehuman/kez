

>>> from melba.ui.application import UI
>>> ui = UI()
>>> try:
...     ui.run([])
... except SystemExit:
...     pass
usage: py.test [--version] [-v] [--log-file LOG_FILE] [-q] [-h] [--debug]
               [-d DATA_PATH]
<BLANKLINE>
Static Document Builder.
<BLANKLINE>
optional arguments:
  --version             show program's version number and exit
  -v, --verbose         Increase verbosity of output. Can be repeated.
  --log-file LOG_FILE   Specify a file to log output. Disabled by default.
  -q, --quiet           suppress output except warnings and errors
  -h, --help            show this help message and exit
  --debug               show tracebacks on errors
  -d DATA_PATH, --data-path DATA_PATH
                        the path to an sqlite database (defaults to
                        '~/.melba/data.db')
<BLANKLINE>
Commands:
  add            Add a new project
  build          Build project documents
  complete       print bash completion command
  help           print detailed help for another command
  list           List all documents in each project
  serve          Open a HTML document in a browser


No projects are defined so `melba list` returns nothing.

>>> try:
...     ui.run(["list"])
... except SystemExit:
...     pass


Add a project with `melba add <name> <repository>`.

>>> try:
...     ui.run(["add", "myblog", "git@github.com:averagehuman/maths.averagehuman.org.git"])
... except SystemExit:
...     pass


>>> try:
...     ui.run(["list"])
... except SystemExit:
...     pass

