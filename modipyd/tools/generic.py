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

You can specify startup file by one of these ways:

1. Setting an environment variable named $MODIPYDRC to
   the name of a file containing your start-up commands.
   This is similar to the .profile feature of the Unix shells.

2. Putting ``modipydrc`` or ``.modipydrc`` file in the current
   directory. Modipyd looks these files and executes it if exists.

3. Using ``--rcfile`` command option to specify the name of
   a file containing your start-up commands.

Each process is applied in order. That means, if one process alters
a variable and a second process alters a variable with the same name,
the second will override the first.


    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""
import os
import sys
import logging
from optparse import OptionParser

from modipyd import LOGGER
from modipyd.application import Application


# ----------------------------------------------------------------
# Version
# ----------------------------------------------------------------
MAJOR_VERSION = 0
MINOR_VERSION = 1
VERSION_STRING = "%d.%d" % (MAJOR_VERSION, MINOR_VERSION)

STARTUP_ENVIRON_NAME = 'MODIPYDRC'
STARTUP_FILENAMES = ['modipydrc', '.modipydrc']


def startup_files(rcfile):
    if STARTUP_ENVIRON_NAME in os.environ:
        f = os.environ[STARTUP_ENVIRON_NAME]
        if os.path.isfile(f):
            yield f

    for f in STARTUP_FILENAMES:
        if os.path.isfile(f):
            yield f

    if rcfile and os.path.isfile(rcfile):
        yield rcfile

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

    # Load configuration (startup) file
    for rcfile in startup_files(options.rcfile):
        LOGGER.info("Loading startup file from %s" % rcfile)
        execfile(rcfile, globals(), {'application': application})

    return application

def make_option_parser():
    parser = OptionParser(
        usage="usage: %prog [options] [files or directories]",
        version=("%prog " + VERSION_STRING))

    parser.add_option("-v", "--verbose",
        action="count", dest="verbosity", default=0,
        help="make the operation more talkative")
    parser.add_option("-x", "--plugin", default=[],
        action="append", dest="plugins", metavar='PLUGIN_NAME',
        help="qualified name of the plugin, "
             "the plugin must be callable object (e.g. function, class).")
    parser.add_option("--rcfile", default=None,
        action="store", dest="rcfile", metavar='FILE',
        help="specify a startup script. "
             "Modipyd also looks $%s environment variable, and "
             "%s files in current directory" % (STARTUP_ENVIRON_NAME, 
             ', '.join(STARTUP_FILENAMES)))

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
