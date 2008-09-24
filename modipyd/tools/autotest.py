"""
autotest
================================================

quoted from http://www.zenspider.com/ZSS/Products/ZenTest/

> Improves feedback by running tests continuously.
> Continually runs tests based on files you've changed.
> Get feedback as soon as you save. Keeps you in your editor
> allowing you to get stuff done faster.
> Focuses on running previous failures until you've fixed them.

    :copyright: 2008 by Takanori Ishikawa <takanori.ishikawa@gmail.com>
    :license: MIT (See ``LICENSE`` file for more details)

"""
import os
import sys
import logging
import unittest
from optparse import OptionParser

from modipyd import LOGGER
from modipyd.monitor import Monitor


# ----------------------------------------------------------------
# Version
# ----------------------------------------------------------------
MAJOR_VERSION = 0
MINOR_VERSION = 1
VERSION_STRING = "%d.%d" % (MAJOR_VERSION, MINOR_VERSION)


# ----------------------------------------------------------------
# Notification Observer
# ----------------------------------------------------------------
def scan_code(co, module):
    import pprint

    print "Scan", module.name
    code = co.co_code
    pprint.pprint(co.co_consts)


def observe(module_descriptor):

    # Walking dependency graph in imported module to
    # module imports order.
    for descriptor in module_descriptor.walk():

        LOGGER.info("-> Affected: %s" % descriptor.name)

        # We can't use ``unittest.TestLoader`` to loading tests,
        # bacause ``TestLoader`` imports (execute) module code.
        # If imported/executed module have a statement such as
        # ``sys.exit()``, ...program exit!

        modcode = module_descriptor.module_code
        scan_code(modcode.code, modcode)

        # FIXME: But depending on filename is maybe a bad idea.
        filename = os.path.basename(descriptor.filename)
        if filename.startswith('test_'):
            LOGGER.info("=> Loading:  %s" % descriptor.name)


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def main(options, filepath):
    """
    Monitoring modules on the search path ``path``. If ``path`` is
    a list of directory names, each directory is searched for files
    with '.py' suffix. They are also inserted into ``sys.path`` so that
    program can import monitoring modules.
    """
    # options handling
    if options.verbose:
        LOGGER.setLevel(logging.INFO)
    if options.debug:
        LOGGER.setLevel(logging.DEBUG)

    # So many projects contain its modules and packages
    # at top level directory, modipyd inserts current directory
    # in ``sys.path`` module search path variable for convenience.
    sys.path.insert(0, os.getcwd())

    # start monitoring
    try:

        monitor = Monitor(filepath)
        for modified in monitor.start():
            LOGGER.info("Modified:\n%s" % modified.describe(indent=4))
            observe(modified)

    except KeyboardInterrupt:
        LOGGER.debug('KeyboardInterrupt', exc_info=True)

def run():
    """Standalone program interface"""
    parser = OptionParser(
        usage="usage: %prog [options] [files or directories]",
        version=("%prog " + VERSION_STRING))

    parser.add_option("-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="Make the operation more talkative")
    parser.add_option("--debug",
        action="store_true", dest="debug", default=False,
        help="Make the operation more talkative (debug mode)")

    (options, args) = parser.parse_args()
    main(options, args or '.')


if __name__ == '__main__':
    run()
