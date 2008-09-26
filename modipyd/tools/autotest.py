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

from modipyd import LOGGER, utils
from modipyd.monitor import Monitor
from modipyd.analysis import has_subclass


# ----------------------------------------------------------------
# Version
# ----------------------------------------------------------------
MAJOR_VERSION = 0
MINOR_VERSION = 1
VERSION_STRING = "%d.%d" % (MAJOR_VERSION, MINOR_VERSION)


# ----------------------------------------------------------------
# UnitTest
# ----------------------------------------------------------------
def collect_unittest(module_names):
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for name in module_names:
        try:
            module = utils.import_module(name)
        except ImportError:
            LOGGER.warn(
                "ImportError occurred while loading module",
                exc_info=True)
        else:
            tests = loader.loadTestsFromModule(module)
            if tests.countTestCases():
                suite.addTest(tests)
                LOGGER.info("Found unittest.TestCase: %s" % module.__name__)
    return suite

def run_unittest(suite):
    if suite.countTestCases():
        runner = unittest.TextTestRunner()
        runner.run(suite)

def spawn_unittest_runner(testables):
    args = [sys.executable] + sys.argv
    for t in testables:
        args.append("-x")
        args.append(t.name)

    if sys.platform == "win32":
        # Avoid argument parsing problem in
        # windows, DOS platform
        args = ['"%s"' % arg for arg in args]

    LOGGER.info(
        "Spawn test runner process: %s" % ' '.join(args))
    return os.spawnve(os.P_WAIT, sys.executable, args, os.environ.copy())


# ----------------------------------------------------------------
# Notification Observer
# ----------------------------------------------------------------
def observe(module_descriptor):

    # Walking dependency graph in imported module to
    # module imports order.
    testables = []
    for descriptor in module_descriptor.walk():
        LOGGER.info("-> Affected: %s" % descriptor.name)
        if has_subclass(descriptor, unittest.TestCase):
            testables.append(descriptor)

    # Runntine tests
    if testables:
        spawn_unittest_runner(testables)


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
    if options.verbosity > 0:
        LOGGER.setLevel(logging.INFO)
    if options.verbosity > 1:
        LOGGER.setLevel(logging.DEBUG)

    # So many projects contain its modules and packages
    # at top level directory, modipyd inserts current directory
    # in ``sys.path`` module search path variable for convenience.
    sys.path.insert(0, os.getcwd())

    if options.tests:
        # Test runner mode, no monitoring
        suite = collect_unittest(options.tests)
        run_unittest(suite)
    else:
        # start monitoring
        try:

            monitor = Monitor(filepath)
            for modified in monitor.start():
                LOGGER.info("Modified:\n%s" % modified.describe(indent=4))
                observe(modified)

        except KeyboardInterrupt:
            LOGGER.debug('KeyboardInterrupt', exc_info=True)

def make_option_parser():
    parser = OptionParser(
        usage="usage: %prog [options] [files or directories]",
        version=("%prog " + VERSION_STRING))

    parser.add_option("-v", "--verbose",
        action="count", dest="verbosity", default=0,
        help="Make the operation more talkative")
    parser.add_option("-x", "--tests",
        action="append", dest="tests", default=[], type='string',
        help="Execute testcase module")

    return parser


def run():
    """Standalone program interface"""
    parser = make_option_parser()
    (options, args) = parser.parse_args()
    main(options, args or '.')


if __name__ == '__main__':
    run()
