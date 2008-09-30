"""
Modipyd command interface
================================================


The Startup Script
------------------------------------------------
When you use ``modipud`` command, it is frequently handy to have
some standard commands executed every time the command is started.

For example, you can add the custom BytecodeProcessor in this.file:

    from modipyd import BYTECODE_PROCESSORS
    BYTECODE_PROCESSORS.append('myprocessor.MyBytecodeProcessor')

In the startup script, ``application`` variable in scope points
``modipyd.application.Application`` instance. So you can install plugins
manually:

    from myplugins import MyGreatPlugin
    application.install_plugin(MyGreatPlugin)

There are three files where program will search for startup file,
in the following order:

1. An environment variable named ``$MODIPYDRC`` to the name of
   a file containing your start-up commands.

2. ``modipydrc`` or ``.modipydrc`` file in the current
   directory. Modipyd looks these files and executes it if exists.

3. ``--rcfile`` command option to specify the name of a file
   containing your start-up commands.

The most recently found startup file has highest priority. For example,
if a startup file is given on command line (``--rcfile`` option), other
startup files will be ignored. 

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

import os
import sys
import logging
from optparse import OptionParser

from modipyd import LOGGER, __version__
from modipyd.application import Application


# ----------------------------------------------------------------
# Startup files
# ----------------------------------------------------------------
STARTUP_ENVIRON_NAME = 'MODIPYDRC'
STARTUP_FILENAMES = ['modipydrc', '.modipydrc']


def find_startup_files(environ=None, rcfile=None):
    if rcfile and os.path.isfile(rcfile):
        return [rcfile]
    for rcfile in STARTUP_FILENAMES:
        if os.path.isfile(rcfile):
            return [rcfile]
    if environ and STARTUP_ENVIRON_NAME in environ:
        rcfile = environ[STARTUP_ENVIRON_NAME]
        if os.path.isfile(rcfile):
            return [rcfile]
    return []

def make_application(options, filepath):
    # options handling
    if options.verbosity > 0:
        LOGGER.setLevel(logging.INFO)
    if options.verbosity > 1:
        LOGGER.setLevel(logging.DEBUG)

    # So many projects contain its modules and packages at
    # the top level directory, modipyd inserts current directory
    # in ``sys.path`` module search path variable for convenience.
    sys.path.insert(0, os.getcwd())

    # Create Application instance, Install plugins
    application = Application(filepath)
    for plugin in options.plugins:
        application.install_plugin(plugin)

    # Predefine variables
    variables = {}
    for var in options.defines:
        i = var.find('=')
        if i == -1:
            variables[var] = ''
        else:
            variables[var[:i]] = var[i+1:]

    if variables:
        import pprint
        application.update_variables(variables)
        LOGGER.info(
            "Predefined variables: %s" % pprint.pformat(variables))

    # Load configuration (startup) file
    for rcfile in find_startup_files(os.environ, options.rcfile):
        LOGGER.info("Loading startup file from %s" % rcfile)
        execfile(rcfile, globals(), {'application': application})

    return application

def make_option_parser():
    parser = OptionParser(
        usage="usage: %prog [options] [files or directories]",
        version=("%prog " + __version__))

    parser.add_option("-v", "--verbose",
        action="count", dest="verbosity", default=0,
        help="make the operation more talkative")
    parser.add_option("-x", "--plugin", default=[],
        action="append", dest="plugins", metavar='PLUGIN_NAME',
        help="qualified name of the plugin, "
             "the plugin must be callable object (e.g. function, class).")
    parser.add_option("--rcfile", default=None,
        action="store", dest="rcfile", metavar='FILE',
        help="specify a startup script. If a startup file is given on "
             "command line, other startup files will be ignored. "
             "Modipyd also looks $%s environment variable, and "
             "%s files in current directory" % (STARTUP_ENVIRON_NAME, 
             ', '.join(STARTUP_FILENAMES)))
    parser.add_option("-D", default=[],
        action="append", dest="defines", metavar='name(=value)',
        help="predefine name as a plugin context variable, "
             "with specified value string (or empty string if omitted).")

    return parser

def run():
    """Standalone program interface"""
    parser = make_option_parser()
    (options, args) = parser.parse_args()

    application = make_application(options, args or '.')
    try:
        application.run()
    except KeyboardInterrupt:
        LOGGER.debug('Keyboard Interrupt', exc_info=True)


if __name__ == '__main__':
    run()
