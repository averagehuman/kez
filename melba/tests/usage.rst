

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
  list           List all projects
  serve          Open a HTML document in a browser


