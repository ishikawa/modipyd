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
from modipyd import utils, monitor


# ----------------------------------------------------------------
# Version
# ----------------------------------------------------------------
MAJOR_VERSION = 0
MINOR_VERSION = 1
VERSION_STRING = "%d.%d" % (MAJOR_VERSION, MINOR_VERSION)


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def run_unittest(suite):
    if suite.countTestCases():
        runner = unittest.TextTestRunner()
        runner.run(suite)

def collect_affected_unittests(module_descriptor):
    from os.path import basename

    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader

    for desc in module_descriptor.walk():
        LOGGER.info("-> Affected: %s" % desc.name)

        # TODO: Don't depends on filename pattern
        if basename(desc.filepath).startswith('test_'):
            module = desc.import_module()
            tests = loader.loadTestsFromModule(module)
            if tests.countTestCases():
                suite.addTest(tests)
                LOGGER.info("Running test: %s" % module.__name__)

    return suite


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
        for modified in monitor.monitor(filepath):
            LOGGER.info("Modified:\n%s" % modified.describe(indent=4))
            suite = collect_affected_unittests(modified)
            run_unittest(suite)

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
