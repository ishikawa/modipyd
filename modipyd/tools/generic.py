"""
Generic modipyd command

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


def make_application(options, filepath):
    # options handling
    if options.verbosity > 0:
        LOGGER.setLevel(logging.INFO)
    if options.verbosity > 1:
        LOGGER.setLevel(logging.DEBUG)

    # So many projects contain its modules and packages
    # at top level directory, modipyd inserts current directory
    # in ``sys.path`` module search path variable for convenience.
    sys.path.insert(0, os.getcwd())

    # Create Runner instance, install plugins
    application = Application(filepath)
    for plugin in options.plugins:
        application.install_plugin(plugin)
    return application

def make_option_parser():
    parser = OptionParser(
        usage="usage: %prog [options] [files or directories]",
        version=("%prog " + VERSION_STRING))

    parser.add_option("-v", "--verbose",
        action="count", dest="verbosity", default=0,
        help="make the operation more talkative")
    parser.add_option("-m", "--plugin",
        action="append", dest="plugins", metavar='PLUGIN_NAME',
        help="qualified name of the plugin, "
             "the plugin must be callable object (e.g. function, class).")
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
