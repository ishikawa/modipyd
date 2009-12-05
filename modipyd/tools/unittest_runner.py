"""
A command-line program that runs a set of tests; this is primarily for making
test modules conveniently executable.

    :copyright: 2008 by Takanori Ishikawa
    :license: MIT, see LICENSE for more details.
"""

import imp
import os
import sys
import unittest
from optparse import OptionParser

from modipyd import LOGGER, utils, resolve
from modipyd.utils import import_component


def collect_unittest(paths):
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    resolver = resolve.ModuleNameResolver()

    for filepath in paths:
        name, package = resolver.resolve(filepath)
        try:
            if package:
                module = utils.import_module(name)
            else:
                module = imp.load_source(name, filepath)
        except ImportError:
            LOGGER.warn(
                "ImportError occurred while loading module",
                exc_info=True)
        else:
            tests = loader.loadTestsFromModule(module)
            if tests.countTestCases():
                suite.addTest(tests)
                LOGGER.info("Found %d test(s) in module '%s'" % (tests.countTestCases(), module.__name__))
            else:
                LOGGER.warn("No tests found in module '%s'" % module.__name__)
    return suite

def main(paths, test_runner_class='unittest.TextTestRunner'):
    suite = collect_unittest(paths)
    if not suite.countTestCases():
        return
    
    testRunner = import_component(test_runner_class)
    runner = testRunner()
    runner.run(suite)


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] file1, file2, ...")
    parser.add_option("-r", "--runner", default='unittest.TextTestRunner',
        action="store", dest="runner", metavar='CLASS_NAME',
        help="qualified name of the unittest.TestRunner subclass "
             "(default: unittest.TextTestRunner)")
    parser.add_option("--loglevel",
        action="store", type="int", dest="loglevel", metavar='LOG_LEVEL',
        help="Specifies the lowest-severity log message a logger will handle")

    options, args = parser.parse_args()

    if options.loglevel is not None:
        LOGGER.setLevel(options.loglevel)

    sys.path.insert(0, os.getcwd())
    main(args, options.runner)
