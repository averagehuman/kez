

>>> from kez.ui.application import UI
>>> ui = UI()

Run without parameters, **kez** prints the help message:

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
                        '~/.kez/data.db')
<BLANKLINE>
Commands:
  add            Add a new project
  build          Build project documents
  complete       print bash completion command
  help           print detailed help for another command
  list           List all documents in each project
  reset          Remove all data
  serve          Open a HTML document in a browser

Create a temporary database for what follows.

>>> import tempfile, shlex
>>> data_file, data_path = tempfile.mkstemp(prefix="kez-test-database")
>>> def run(command):
...     try:
...         return ui.run(["-d", data_path] + shlex.split(command))
...     except SystemExit:
...         pass

No projects are defined so **kez list** returns nothing.

>>> run("list")
<BLANKLINE>
0


Add a project with **kez add <name> <repository>**.

>>> run("add myblog git@github.com:averagehuman/maths.averagehuman.org.git")
0


>>> run("list")
+---------+------------------------+---------+--------------------------------------------------------+
| Project | Document               | Type    | Url                                                    |
+---------+------------------------+---------+--------------------------------------------------------+
| myblog  | maths.averagehuman.org | PELICAN | git@github.com:averagehuman/maths.averagehuman.org.git |
+---------+------------------------+---------+--------------------------------------------------------+
0


Build the document:

>>> run("build myblog") # doctest: +ELLIPSIS
***** STARTED BUILDING: [myblog] maths.averagehuman.org  *****
...

If a root *index.html* has been successfully created, you can now view the
document locally with **kez serve myblog**.

Remove the kez database with **kez reset**:

>>> import os
>>> os.path.exists(data_path)
True
>>> run("reset")
Database removed.
0
>>> os.path.exists(data_path)
False

