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
import time
import logging
import unittest
from optparse import OptionParser

from modipyd import LOGGER
from modipyd.pyscript import PyScript
from modipyd import utils


# ----------------------------------------------------------------
# Version
# ----------------------------------------------------------------
MAJOR_VERSION = 0
MINOR_VERSION = 1
VERSION_STRING = "%d.%d" % (MAJOR_VERSION, MINOR_VERSION)


# ----------------------------------------------------------------
# API, Functions, Classes...
# ----------------------------------------------------------------
def collect_pyscript(filepath):
    scripts = []
    for filename in utils.collect_files(filepath):
        if filename.endswith('.py'):
            try:
                modfile = PyScript(filename)
                LOGGER.info("Found: %s" % modfile)
                LOGGER.info("Module Loaded: %s" % modfile.module)
            except os.error:
                LOGGER.warn(
                    "The file at %s does not exist"
                    " or is inaccessible, ignore." % filename)
            except ImportError:
                LOGGER.info("Couldn't import file at %s, ignore" % filename)
            else:
                scripts.append(modfile)

    # uniqfy
    return list(set(scripts))


def monitor(scripts):
    """WARNING: This method can modify ``scripts`` list."""
    assert isinstance(scripts, list)
    while scripts:
        time.sleep(1)
        # For in-place deletion (avoids copying the list),
        # Don't delete anything earlier in the list than
        # the current element through.
        for i, script in enumerate(reversed(scripts)):
            if not os.path.exists(script.filename):
                del script[-i]
            elif script.update():
                yield script


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def collect_unittest(scripts):
    """
    Search ``unittest.TestCase`` classes in scripts,
    return ``unittest.TestSuite`` instance.
    """
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for script in scripts:
        tests = loader.loadTestsFromModule(script.module)
        suite.addTest(tests)
    return suite

def run_unittest(scripts):
    suite = collect_unittest(scripts)
    runner = unittest.TextTestRunner()
    runner.run(suite)

def spawn_unittest_runner():
    args = [sys.executable] + sys.argv
    args.append("--run-tests")

    if sys.platform == "win32":
        args = ['"%s"' % arg for arg in args]

    LOGGER.debug("Spawn test runner process")
    return os.spawnve(os.P_WAIT, sys.executable, args, os.environ.copy())

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

    # start monitoring
    try:
        # Make filepath iterable.
        filepath = utils.wrap_sequence(filepath)
        assert not isinstance(filepath, basestring)

        # absolute path convertion
        filepath = [os.path.abspath(f) for f in filepath]
        scripts = collect_pyscript(filepath)

        # test runner mode
        if options.run_tests:
            LOGGER.info("Test Runner Mode: %d" % os.getpid())
            run_unittest(scripts)
        else:
            for modified in monitor(scripts):
                LOGGER.info("Modified %s" % modified)
                spawn_unittest_runner()

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

    parser.add_option("--run-tests",
        action="store_true", dest="run_tests", default=False,
        help="Test runner mode")

    (options, args) = parser.parse_args()
    main(options, args or os.getcwd())


if __name__ == '__main__':
    run()
