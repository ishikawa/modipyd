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

from modipyd import LOGGER, collect_files
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
    for filename in collect_files(filepath):
        if filename.endswith('.py'):
            try:
                modfile = PyScript(filename)
                #print modfile.module
                LOGGER.info("Found: %s" % filename)
            except os.error:
                LOGGER.warn(
                    "The file at %s does not exist"
                    " or is inaccessible, ignore." % filename)
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

        # Insert directories path into the head of ``sys.path``
        # so that ``monitor()`` can import found modules.
        # Notes: For the proper order of specified filepaths,
        # inserts path in reverse order.
        for f in reversed(filepath):
            assert os.path.isabs(f)
            if os.path.isdir(f):
                sys.path.insert(0, f)
                LOGGER.info("sys.path: %s" % f)

        scripts = collect_pyscript(filepath)
        for modified in monitor(scripts):
            LOGGER.info("Modified %s" % modified)
            print sys.modules
            run_unittest(scripts)

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
    main(options, args or os.getcwd())


if __name__ == '__main__':
    run()
